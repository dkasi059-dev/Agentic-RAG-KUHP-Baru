import os
import re
import streamlit as st
from typing import TypedDict, List, Optional
from langchain_core.tools import Tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END
from langsmith import traceable
from langchain_openai import ChatOpenAI

# ================================
# 🔧 Konfigurasi Awal
# ================================
os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]
os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]

# ================================
# 🔮 Setup OpenRouter
# ================================
llm = ChatOpenAI(
    model="openrouter/free",
    temperature=0,
    max_tokens=1200,
    openai_api_key=st.secrets["API_OR"],
    openai_api_base="https://openrouter.ai/api/v1"
)

# ================================
# 🧰 Tools Bahasa Indonesia
# ================================
wikipedia_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(lang="id")
)

arxiv_tool = ArxivQueryRun(
    api_wrapper=ArxivAPIWrapper()
)

tavily_tool_instance = TavilySearch(
    max_results=3
)

tools = {
    "Wikipedia": Tool(
        name="Wikipedia",
        func=wikipedia_tool.run,
        description="Konsep umum yang berkaitan dengan KUHP Baru."
    ),
    "arXiv": Tool(
        name="arXiv",
        func=arxiv_tool.run,
        description="Penelitian akademik yang berkaitan dengan KUHP Baru."
    ),
    "TavilySearch": Tool(
        name="TavilySearch",
        func=tavily_tool_instance.run,
        description="Berita, peraturan, putusan, dan perkembangan hukum Indonesia terkait KUHP Baru."
    )
}

# ================================
# 📚 Load Dokumen KUHP Baru
# ================================
with open("KUHP_Baru.txt", "r", encoding="utf-8") as f:
    documents = [f.read()]

# ================================
# 🧩 Agent State
# ================================
class AgentState(TypedDict):
    question: str
    conversation_history: Optional[List[dict]]
    docs: Optional[List[str]]
    external_docs: Optional[List[str]]
    answer: Optional[str]
    relevant: Optional[bool]
    answered: Optional[bool]
    selected_tools: Optional[List[str]]
    reasoning: Optional[str]]
    out_of_scope: Optional[bool]

# ================================
# 🧠 Conversation Memory
# ================================
def format_conversation_history(
    history: Optional[List[dict]],
    max_messages: int = 8
) -> str:
    if not history:
        return "Belum ada percakapan sebelumnya."

    recent_history = history[-max_messages:]
    formatted = []

    for message in recent_history:
        role = message.get("role", "")
        text = message.get("text", "")

        if not text:
            continue

        if role == "user":
            label = "Pengguna"
        else:
            label = "Asisten"

        # Batasi panjang setiap pesan agar hemat token
        text = str(text)[:1500]
        formatted.append(f"{label}: {text}")

    return "\n".join(formatted)

# ================================
# 🚦 Scope Gate
# Tidak menggunakan LLM
# ================================
KUHP_KEYWORDS = {
    "kuhp",
    "kitab undang-undang hukum pidana",
    "hukum pidana",
    "pidana",
    "tindak pidana",
    "delik",
    "kejahatan",
    "pelanggaran",
    "pemidanaan",
    "pidana mati",
    "pidana penjara",
    "pidana denda",
    "pidana tambahan",
    "pidana pokok",
    "sanksi pidana",
    "hukuman pidana",
    "tersangka",
    "terdakwa",
    "terpidana",
    "pembunuhan",
    "penganiayaan",
    "pencurian",
    "penipuan",
    "pemalsuan",
    "pemerkosaan",
    "perzinaan",
    "perzinahan",
    "pencabulan",
    "korupsi",
    "suap",
    "penggelapan",
    "perampasan",
    "percobaan tindak pidana",
    "penyertaan",
    "pembelaan terpaksa",
    "alasan pembenar",
    "alasan pemaaf",
    "pertanggungjawaban pidana",
    "kesalahan",
    "kesengajaan",
    "kealpaan",
    "peraturan pidana",
    "pasal pidana"
}

def is_kuhp_related(question: str) -> bool:
    q = question.lower().strip()

    # Pertanyaan lanjutan yang sangat pendek dianggap
    # masih berkaitan dengan percakapan sebelumnya.
    follow_up = {
        "bagaimana sanksinya",
        "apa sanksinya",
        "berapa dendanya",
        "pasal berapa",
        "jelaskan lebih lanjut",
        "bagaimana penerapannya",
        "siapa yang dimaksud",
        "apa maksudnya",
        "bagaimana dengan itu",
        "kalau begitu bagaimana",
        "lalu bagaimana",
        "bagaimana hukumnya",
        "apa hukumannya",
        "apa akibatnya"
    }

    if q in follow_up:
        return True

    return any(keyword in q for keyword in KUHP_KEYWORDS)

# ================================
# 🚦 Node: Scope Check
# ================================
@traceable
def scope_check_node(state: AgentState) -> AgentState:
    q = state["question"]

    related = is_kuhp_related(q)

    if not related:
        return {
            **state,
            "out_of_scope": True,
            "answer": (
                "saya tidak bisa menjawab pertanyaan Anda karena "
                "tidak berkaitan dengan Kitab Undang-Undang Hukum Pidana "
                "(KUHP) baru"
            ),
            "answered": True
        }

    return {
        **state,
        "out_of_scope": False
    }

# ================================
# 🧠 Node: Tool Selection
# ================================
@traceable
def tool_selection_node(state: AgentState) -> AgentState:
    q = state["question"]

    conversation_history = state.get(
        "conversation_history",
        []
    )

    conversation_context = format_conversation_history(
        conversation_history
    )

    prompt = f"""
Kamu adalah asisten ahli Kitab Undang-Undang Hukum Pidana (KUHP) Baru Indonesia.

Tentukan sumber eksternal yang diperlukan untuk pertanyaan berikut.

Riwayat:
{conversation_context}

Pertanyaan:
{q}

Tools:
1. Wikipedia = konsep umum
2. arXiv = penelitian akademik
3. TavilySearch = berita/peraturan/putusan terbaru

Aturan:
- Utamakan KUHP_Baru.txt.
- Gunakan tools hanya jika benar-benar diperlukan.
- Jika pertanyaan dapat dijawab dari KUHP_Baru.txt, jangan pilih tools eksternal.
- Pilih sesedikit mungkin tools.

Format wajib:
TOOLS: tool1,tool2
REASONING: alasan singkat
"""

    result = llm.invoke(prompt)

    content = str(result.content).strip()
    lines = content.splitlines()

    tools_selected = []
    reasoning = ""

    for line in lines:
        if line.startswith("TOOLS:"):
            raw_tools = line.replace("TOOLS:", "").strip()

            if raw_tools:
                tools_selected = [
                    t.strip()
                    for t in raw_tools.split(",")
                    if t.strip() in tools
                ]

        elif line.startswith("REASONING:"):
            reasoning = line.replace(
                "REASONING:",
                ""
            ).strip()

    return {
        **state,
        "selected_tools": tools_selected,
        "reasoning": reasoning
    }

# ================================
# 🔍 Local Document Retrieval
# Tidak menggunakan LLM
# ================================
def retrieve_relevant_document(
    question: str,
    max_chunks: int = 4,
    chunk_size: int = 3500
) -> List[str]:

    text = documents[0]

    # Pecah berdasarkan paragraf
    paragraphs = [
        p.strip()
        for p in re.split(r"\n\s*\n", text)
        if p.strip()
    ]

    query_words = {
        word
        for word in re.findall(
            r"\b[a-zA-ZÀ-ÿ0-9]+\b",
            question.lower()
        )
        if len(word) >= 3
    }

    scored = []

    for paragraph in paragraphs:
        paragraph_lower = paragraph.lower()

        score = sum(
            1
            for word in query_words
            if word in paragraph_lower
        )

        if score > 0:
            scored.append(
                (score, paragraph)
            )

    scored.sort(
        key=lambda x: x[0],
        reverse=True
    )

    selected = []

    for _, paragraph in scored[:max_chunks]:
        if len(paragraph) > chunk_size:
            paragraph = paragraph[:chunk_size]

        selected.append(paragraph)

    # Jika tidak ditemukan keyword,
    # kirim sebagian kecil dokumen saja.
    if not selected:
        selected = [text[:chunk_size]]

    return selected

# ================================
# 🔍 Node: Multi Source Retrieval
# ================================
@traceable
def multi_source_retrieve_node(state: AgentState) -> AgentState:
    q = state["question"]
    selected = state.get("selected_tools", [])

    # Hanya ambil bagian dokumen yang relevan
    internal_docs = retrieve_relevant_document(q)

    external_docs = []

    for tool_name in selected:
        if tool_name not in tools:
            continue

        try:
            result = tools[tool_name].run(q)

            if isinstance(result, list):
                result_str = ""

                for i, item in enumerate(result):
                    if isinstance(item, dict):
                        result_str += (
                            f"Result {i + 1}: "
                            f"{item.get('title', 'No title')} - "
                            f"{item.get('content', 'No content')}\n"
                        )
                    else:
                        result_str += (
                            f"Result {i + 1}: "
                            f"{str(item)}\n"
                        )

                external_docs.append(
                    result_str[:5000]
                )

            else:
                external_docs.append(
                    str(result)[:5000]
                )

        except Exception as e:
            external_docs.append(
                f"{tool_name} gagal: {str(e)}"
            )

    return {
        **state,
        "docs": internal_docs,
        "external_docs": external_docs
    }

# ================================
# 🧮 Node: Grade Relevance
# Lokal, tanpa LLM
# ================================
@traceable
def enhanced_grade_node(state: AgentState) -> AgentState:
    q = state["question"].lower()

    all_docs = (
        state.get("docs", []) +
        state.get("external_docs", [])
    )

    if not all_docs:
        return {
            **state,
            "relevant": False
        }

    query_words = {
        word
        for word in re.findall(
            r"\b[a-zA-ZÀ-ÿ0-9]+\b",
            q
        )
        if len(word) >= 3
    }

    document_text = " ".join(
        all_docs
    ).lower()

    matches = sum(
        1
        for word in query_words
        if word in document_text
    )

    return {
        **state,
        "relevant": matches >= 1
    }

# ================================
# 🧩 Node: Generate Final Answer
# ================================
@traceable
def enhanced_generation_node(state: AgentState) -> AgentState:
    q = state["question"]

    conversation_history = state.get(
        "conversation_history",
        []
    )

    conversation_context = format_conversation_history(
        conversation_history
    )

    context = "\n\n".join(
        state.get("docs", []) +
        state.get("external_docs", [])
    )

    # Batasi context total
    context = context[:14000]

    prompt = f"""
Kamu adalah asisten ahli Kitab Undang-Undang Hukum Pidana (KUHP) Baru Indonesia.

RIWAYAT PERCAKAPAN:
{conversation_context}

PERTANYAAN TERBARU:
{q}

SUMBER:
{context}

ATURAN:
- Jawab hanya mengenai KUHP Baru.
- Gunakan riwayat percakapan untuk memahami pertanyaan lanjutan.
- Utamakan KUHP_Baru.txt.
- Jangan mengarang pasal, ayat, sanksi, angka, atau ketentuan hukum.
- Jika informasi tidak tersedia dalam sumber, katakan secara jujur.
- Gunakan Bahasa Indonesia formal, ringkas, jelas, dan langsung.
- Sebutkan sumber jika tersedia.

JAWAB:
"""

    res = llm.invoke(prompt)

    return {
        **state,
        "answer": str(res.content).strip()
    }

# ================================
# 🔁 Node: Answer Check
# Lokal, tanpa LLM
# ================================
@traceable
def answer_check_node(state: AgentState) -> AgentState:
    answer = state.get(
        "answer",
        ""
    ).strip()

    relevant = state.get(
        "relevant",
        False
    )

    answered = bool(
        answer and relevant
    )

    return {
        **state,
        "answered": answered
    }

# ================================
# 🔧 Workflow Graph
# ================================
workflow = StateGraph(AgentState)

workflow.add_node(
    "ScopeCheck",
    scope_check_node
)

workflow.add_node(
    "ToolSelection",
    tool_selection_node
)

workflow.add_node(
    "Retrieve",
    multi_source_retrieve_node
)

workflow.add_node(
    "Grade",
    enhanced_grade_node
)

workflow.add_node(
    "Generate",
    enhanced_generation_node
)

workflow.add_node(
    "Evaluate",
    answer_check_node
)

# ================================
# 🚦 Entry
# ================================
workflow.set_entry_point(
    "ScopeCheck"
)

# ================================
# 🚦 Scope Routing
# ================================
workflow.add_conditional_edges(
    "ScopeCheck",
    lambda s: (
        "OutOfScope"
        if s.get("out_of_scope")
        else "InScope"
    ),
    {
        "OutOfScope": END,
        "InScope": "ToolSelection"
    }
)

# ================================
# 🔗 Main Pipeline
# ================================
workflow.add_edge(
    "ToolSelection",
    "Retrieve"
)

workflow.add_edge(
    "Retrieve",
    "Grade"
)

workflow.add_edge(
    "Grade",
    "Generate"
)

workflow.add_edge(
    "Generate",
    "Evaluate"
)

# Tidak ada loop kembali ke Retrieve.
# Ini mencegah pemborosan token dan infinite loop.
workflow.add_edge(
    "Evaluate",
    END
)

# ================================
# 🚀 Compile
# ================================
runnable_graph = workflow.compile()
