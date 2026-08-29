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
    model="cohere/north-mini-code:free",
    temperature=0,
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

tavily_tool_instance = TavilySearch(max_results=3)

tools = {
    "Wikipedia": Tool(
        name="Wikipedia",
        func=wikipedia_tool.run,
        description="Gunakan untuk menemukan konsep umum yang berkaitan dengan Kitab Undang-Undang Hukum Pidana (KUHP) Baru."
    ),
    "arXiv": Tool(
        name="arXiv",
        func=arxiv_tool.run,
        description="Gunakan untuk penelitian akademik yang berkaitan dengan Kitab Undang-Undang Hukum Pidana (KUHP) Baru."
    ),
    "TavilySearch": Tool(
        name="TavilySearch",
        func=tavily_tool_instance.run,
        description="Gunakan untuk informasi terbaru, peraturan Indonesia, berita hukum, dan putusan pengadilan yang berkaitan dengan KUHP Baru."
    )
}

# ================================
# 📚 Load Dokumen KUHP Baru
# ================================
with open("KUHP_Baru.txt", "r", encoding="utf-8") as f:
    kuhp_text = f.read()

documents = [kuhp_text]

# ================================
# 🧩 Define Agent State
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
    reasoning: Optional[str]
    article_number: Optional[int]
    article_text: Optional[str]
    direct_article: Optional[bool]
    use_tools: Optional[bool]

# ================================
# 🧠 MEMORY
# ================================
def format_conversation_history(history):
    if not history:
        return "Tidak ada percakapan sebelumnya."

    formatted = []

    for msg in history[-8:]:
        role = msg.get("role", "")
        text = msg.get("text", "").strip()

        if not text:
            continue

        if role == "user":
            formatted.append(f"Pengguna: {text}")
        elif role in ["assistant", "Asisten"]:
            formatted.append(f"Asisten: {text}")

    if not formatted:
        return "Tidak ada percakapan sebelumnya."

    return "\n".join(formatted)

# ================================
# 🔎 EKSTRAK NOMOR PASAL
# ================================
def detect_article_number(question):
    patterns = [
        r"\bpasal\s+ke[-\s]?(\d+)\b",
        r"\bpasal\s+(\d+)\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, question.lower())

        if match:
            return int(match.group(1))

    return None

# ================================
# 📚 AMBIL PASAL DARI KUHP_Baru.txt
# ================================
def extract_article(article_number):
    text = kuhp_text

    start_pattern = rf"(?im)^\s*Pasal\s+{article_number}\s*\.?\s*$"
    start_match = re.search(start_pattern, text)

    if not start_match:
        start_pattern = rf"(?im)^\s*Pasal\s+{article_number}\s*\.?"
        start_match = re.search(start_pattern, text)

    if not start_match:
        return None

    start = start_match.start()
    search_start = start_match.end()

    boundary_pattern = (
        r"(?im)^\s*(?:"
        r"Pasal\s+\d+\.?"
        r"|BAB\s+[IVXLCDM0-9]+"
        r"|Bagian\s+(?:Kesatu|Kedua|Ketiga|Keempat|Kelima|Keenam|Ketujuh|Kedelapan|Kesembilan|Kesepuluh|[A-Za-z]+)"
        r"|Paragraf\s+\d+"
        r")\s*$"
    )

    next_boundary = re.search(
        boundary_pattern,
        text[search_start:]
    )

    if next_boundary:
        end = search_start + next_boundary.start()
        article = text[start:end].strip()
    else:
        article = text[start:].strip()

    article = re.sub(r"\n{3,}", "\n\n", article)

    return article.strip()

# ================================
# ✨ FORMAT TAMPILAN PASAL
# ================================
def format_article_answer(article_number, article_text):
    lines = article_text.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if re.fullmatch(
            rf"Pasal\s+{article_number}\.?",
            line,
            re.IGNORECASE
        ):
            continue

        cleaned.append(line)

    if not cleaned:
        return f"### Pasal {article_number}\n\nTeks pasal tidak tersedia."

    result = f"### Pasal {article_number}\n\n"

    for line in cleaned:
        if re.match(r"^\(\d+\)", line):
            result += f"{line}\n\n"
        else:
            result += f"{line}\n\n"

    return result.strip()

# ================================
# 🧠 NODE: VALIDASI OLEH LLM
# ================================
@traceable
def validation_node(state: AgentState) -> AgentState:
    question = state["question"]
    history = format_conversation_history(
        state.get("conversation_history", [])
    )

    prompt = f"""
Kamu adalah komponen penalaran utama dari sebuah AI Agent
untuk Kitab Undang-Undang Hukum Pidana (KUHP) Baru Indonesia.

Tugasmu adalah memahami pertanyaan pengguna berdasarkan
pertanyaan dan riwayat percakapan.

Jangan menggunakan aturan berbasis kata kunci.
Gunakan pemahaman semantik dan konteks percakapan.

RIWAYAT PERCAKAPAN:
{history}

PERTANYAAN TERBARU:
{question}

Tentukan:

1. Apakah pertanyaan pengguna berkaitan dengan KUHP Baru?
2. Apakah pertanyaan merujuk pada pasal tertentu?
3. Jika merujuk pada pasal tertentu, tentukan nomor pasalnya.
4. Apakah pertanyaan membutuhkan tools eksternal?
5. Jika membutuhkan tools, tentukan tools yang paling sesuai.

Tools yang tersedia:
- Wikipedia
- arXiv
- TavilySearch

Pertimbangkan konteks percakapan sebelumnya.
Contohnya, jika pengguna mengatakan "jelaskan hal di atas",
"jelaskan pasal tersebut", atau bentuk rujukan lainnya,
gunakan percakapan sebelumnya untuk memahami maksud pengguna.

Jangan mengarang isi KUHP.
Isi KUHP akan diambil secara terpisah dari dokumen KUHP_Baru.txt.

Berikan hasil hanya dengan format berikut:

SCOPE: YES atau NO
ARTICLE: nomor pasal atau NONE
TOOLS: nama tool atau NONE
REASONING: alasan singkat
"""

    result = llm.invoke(prompt)
    content = result.content.strip()

    scope = None
    article_number = None
    selected_tools = []
    reasoning = ""

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("SCOPE:"):
            value = line.replace("SCOPE:", "").strip().upper()

            if value == "YES":
                scope = True
            elif value == "NO":
                scope = False

        elif line.startswith("ARTICLE:"):
            value = line.replace("ARTICLE:", "").strip()

            if value.upper() != "NONE":
                match = re.search(r"\d+", value)

                if match:
                    article_number = int(match.group())

        elif line.startswith("TOOLS:"):
            value = line.replace("TOOLS:", "").strip()

            if value.upper() != "NONE":
                for tool_name in tools:
                    if tool_name.lower() in value.lower():
                        selected_tools.append(tool_name)

        elif line.startswith("REASONING:"):
            reasoning = line.replace(
                "REASONING:",
                ""
            ).strip()

    # Jika LLM menyatakan di luar cakupan.
    if scope is False:
        return {
            **state,
            "relevant": False,
            "direct_article": False,
            "article_number": None,
            "article_text": None,
            "selected_tools": [],
            "use_tools": False,
            "answer": "saya tidak mengetahui jawaban atas pertanyaan tersebut karena berada di luar konteks KUHP Baru.",
            "reasoning": reasoning or "Pertanyaan dinilai tidak berkaitan dengan KUHP Baru."
        }

    # Jika LLM belum memberikan keputusan yang valid,
    # jangan biarkan agent mengarang jawaban.
    if scope is None:
        return {
            **state,
            "relevant": False,
            "direct_article": False,
            "article_number": None,
            "article_text": None,
            "selected_tools": [],
            "use_tools": False,
            "answer": "Saya tidak dapat menentukan relevansi pertanyaan tersebut dengan KUHP Baru.",
            "reasoning": "Router LLM tidak memberikan keputusan scope yang valid."
        }

    # Jika nomor pasal diketahui, ambil langsung dari dokumen.
    article_text = None

    if article_number is not None:
        article_text = extract_article(article_number)

    return {
        **state,
        "relevant": True,
        "article_number": article_number,
        "article_text": article_text,
        "direct_article": article_number is not None,
        "selected_tools": selected_tools,
        "use_tools": len(selected_tools) > 0,
        "reasoning": reasoning
    }

# ================================
# 🧠 NODE: TOOL SELECTION
# ================================
@traceable
def tool_selection_node(state: AgentState) -> AgentState:
    if not state.get("relevant"):
        return {
            **state,
            "selected_tools": [],
            "use_tools": False
        }

    # Jika pertanyaan pasal, dokumen lokal menjadi sumber utama.
    # Tools tetap boleh digunakan jika LLM sebelumnya memilihnya.
    selected = state.get("selected_tools", [])

    return {
        **state,
        "selected_tools": selected,
        "use_tools": len(selected) > 0
    }

# ================================
# 🔍 NODE: RETRIEVAL
# ================================
@traceable
def multi_source_retrieve_node(state: AgentState) -> AgentState:
    if not state.get("relevant"):
        return {
            **state,
            "docs": [],
            "external_docs": []
        }

    # --------------------------------
    # PASAL -> DOKUMEN LANGSUNG
    # --------------------------------
    if state.get("direct_article"):
        article_text = state.get("article_text")

        if article_text:
            return {
                **state,
                "docs": [article_text],
                "external_docs": []
            }

        return {
            **state,
            "docs": [],
            "external_docs": []
        }

    # --------------------------------
    # PERTANYAAN UMUM
    # --------------------------------
    q = state["question"]
    selected = state.get("selected_tools", [])

    internal_docs = documents
    external_docs = []

    for tool_name in selected:
        if tool_name in tools:
            try:
                result = tools[tool_name].run(q)

                if isinstance(result, list):
                    result_str = ""

                    for i, item in enumerate(result):
                        if isinstance(item, dict):
                            result_str += (
                                f"Result {i+1}: "
                                f"{item.get('title', 'No title')} - "
                                f"{item.get('content', 'No content')}\n"
                            )
                        else:
                            result_str += (
                                f"Result {i+1}: {str(item)}\n"
                            )

                    external_docs.append(result_str.strip())

                else:
                    external_docs.append(str(result))

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
# 🧩 NODE: GENERATE FINAL ANSWER
# ================================
@traceable
def enhanced_generation_node(state: AgentState) -> AgentState:
    # --------------------------------
    # OUT OF SCOPE
    # --------------------------------
    if not state.get("relevant"):
        return state

    # --------------------------------
    # PASAL TIDAK DITEMUKAN
    # --------------------------------
    if state.get("direct_article") and not state.get("article_text"):
        article_number = state.get("article_number")

        return {
            **state,
            "answer": (
                f"### Pasal {article_number}\n\n"
                f"Pasal {article_number} tidak ditemukan dalam "
                f"dokumen **KUHP_Baru.txt** yang digunakan oleh sistem.\n\n"
                f"Sistem tidak menggunakan pengetahuan internal model "
                f"untuk mengarang atau menebak isi pasal tersebut."
            ),
            "reasoning": (
                f"Pasal {article_number} tidak ditemukan dalam "
                f"KUHP_Baru.txt."
            )
        }

    # --------------------------------
    # PASAL DITEMUKAN
    # --------------------------------
    if state.get("direct_article"):
        article_number = state.get("article_number")
        article_text = state.get("article_text")

        question = state["question"]
        history = format_conversation_history(
            state.get("conversation_history", [])
        )

        prompt = f"""
Kamu adalah asisten hukum yang menjelaskan KUHP Baru Indonesia.

Gunakan TEKS PASAL sebagai sumber utama dan otoritatif.

RIWAYAT PERCAKAPAN:
{history}

PERTANYAAN:
{question}

TEKS PASAL {article_number}:
{article_text}

Jelaskan pertanyaan pengguna berdasarkan teks pasal tersebut.

Jangan mengarang.
Jangan menambahkan isi pasal.
Jangan membuat ayat atau ketentuan baru.
Jangan mencampurkan pasal lain.
Jika pengguna meminta bunyi atau isi pasal, tampilkan isi
berdasarkan TEKS PASAL.
Jika pengguna meminta penjelasan, jelaskan berdasarkan
TEKS PASAL dan konteks percakapan.

Gunakan bahasa Indonesia yang formal, rapi, natural,
dan mudah dipahami.

Jangan memberikan informasi yang tidak didukung oleh
TEKS PASAL.
"""

        res = llm.invoke(prompt)

        return {
            **state,
            "answer": res.content.strip()
        }

    # --------------------------------
    # PERTANYAAN UMUM
    # --------------------------------
    q = state["question"]

    history = format_conversation_history(
        state.get("conversation_history", [])
    )

    context = "\n".join(
        state.get("docs", []) +
        state.get("external_docs", [])
    )

    prompt = f"""
Kamu adalah asisten ahli Kitab Undang-Undang Hukum Pidana
(KUHP) Baru Indonesia.

RIWAYAT PERCAKAPAN:
{history}

PERTANYAAN TERBARU:
{q}

SUMBER:
{context}

Jawab pertanyaan berdasarkan sumber yang tersedia.

Utamakan informasi dari KUHP_Baru.txt.
Gunakan sumber eksternal hanya jika memang tersedia
dan relevan.

Jangan mengarang isi hukum.
Jangan membuat nomor pasal.
Jangan membuat bunyi pasal.
Jangan menyatakan suatu fakta hukum sebagai fakta apabila
tidak didukung oleh sumber.

Gunakan konteks percakapan sebelumnya untuk memahami
pertanyaan lanjutan.

Jika sumber tidak memberikan informasi yang cukup,
katakan secara jujur bahwa informasi tersebut tidak
ditemukan dalam sumber yang tersedia.

Jawab dengan bahasa Indonesia formal, rapi, jelas,
natural, dan tidak bertele-tele.
"""

    res = llm.invoke(prompt)

    return {
        **state,
        "answer": res.content.strip()
    }

# ================================
# 🔧 WORKFLOW GRAPH
# ================================
workflow = StateGraph(AgentState)

workflow.add_node(
    "Validation",
    validation_node
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
    "Generate",
    enhanced_generation_node
)

workflow.set_entry_point("Validation")

workflow.add_edge(
    "Validation",
    "ToolSelection"
)

workflow.add_edge(
    "ToolSelection",
    "Retrieve"
)

workflow.add_edge(
    "Retrieve",
    "Generate"
)

workflow.add_edge(
    "Generate",
    END
)

runnable_graph = workflow.compile()
