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
# 🔮 Setup LLM
# ================================
llm = ChatOpenAI(
    model="openrouter/free",
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

tavily_tool_instance = TavilySearch(
    max_results=3
)

tools = {
    "Wikipedia": Tool(
        name="Wikipedia",
        func=wikipedia_tool.run,
        description="Gunakan untuk menemukan konsep utama, sejarah, dan hal-hal lain yang berkaitan dengan Kitab Undang-Undang Hukum Pidana (KUHP) baru dalam Bahasa Indonesia."
    ),
    "arXiv": Tool(
        name="arXiv",
        func=arxiv_tool.run,
        description="Gunakan untuk referensi akademik tentang teori atau penelitian berkaitan dengan Kitab Undang-Undang Hukum Pidana (KUHP) baru."
    ),
    "TavilySearch": Tool(
        name="TavilySearch",
        func=tavily_tool_instance.run,
        description="Gunakan untuk menemukan berita, artikel, peraturan Indonesia, putusan pengadilan, situs hukum, Hukumonline, maupun sumber internet lain yang berkaitan dengan Kitab Undang-Undang Hukum Pidana (KUHP) baru."
    )
}

# ================================
# 📚 Load Dokumen KUHP Baru
# ================================
with open("KUHP_Baru.txt", "r", encoding="utf-8") as f:
    documents = [f.read()]

KUHP_TEXT = documents[0]

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
    reasoning: Optional[str]]
    retry_count: Optional[int]

# ================================
# 🧠 Helper: Format Conversation
# ================================
def format_conversation_history(history):
    if not history:
        return "Belum ada percakapan sebelumnya."

    formatted = []

    for item in history[-8:]:
        role = item.get("role", "")
        text = item.get("text", "")

        if role == "user":
            formatted.append(f"Pengguna: {text}")
        elif role in ["assistant", "Asisten"]:
            formatted.append(f"Asisten: {text}")

    return "\n".join(formatted)

# ================================
# 🔎 Helper: Ambil Nomor Pasal
# ================================
def extract_article_number(question):
    patterns = [
        r"pasal\s+(\d+)",
        r"pasal\s*no\.?\s*(\d+)",
        r"artikel\s+(\d+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, question.lower())
        if match:
            return int(match.group(1))

    return None

# ================================
# 📚 Helper: Cari Pasal Dalam KUHP
# ================================
def find_article_in_kuhp(article_number):
    if article_number is None:
        return None

    pattern = rf"(?im)^\s*Pasal\s+{article_number}\b"

    matches = list(re.finditer(pattern, KUHP_TEXT))

    if not matches:
        return None

    start = matches[0].start()

    next_pattern = r"(?im)^\s*Pasal\s+\d+\b"
    next_match = re.search(next_pattern, KUHP_TEXT[start + 1:])

    if next_match:
        end = start + 1 + next_match.start()
    else:
        end = min(len(KUHP_TEXT), start + 12000)

    article_text = KUHP_TEXT[start:end].strip()

    return article_text

# ================================
# 🧠 Node: Tool Selection
# ================================
@traceable
def tool_selection_node(state: AgentState) -> AgentState:
    q = state["question"]
    history = state.get("conversation_history", [])

    article_number = extract_article_number(q)

    # --------------------------------
    # Jika pertanyaan meminta pasal
    # --------------------------------
    if article_number is not None:
        article = find_article_in_kuhp(article_number)

        if article:
            return {
                **state,
                "selected_tools": ["Documents"],
                "reasoning": f"Pasal {article_number} ditemukan langsung dalam KUHP_Baru.txt.",
                "relevant": True
            }

        # Pasal tidak ditemukan → JANGAN cari-cari atau mengarang
        return {
            **state,
            "selected_tools": [],
            "reasoning": f"Pasal {article_number} tidak ditemukan dalam KUHP_Baru.txt. Sistem tidak akan membuat atau menebak isi pasal.",
            "relevant": True
        }

    # --------------------------------
    # Deteksi permintaan sumber internet
    # --------------------------------
    q_lower = q.lower()

    external_source_keywords = [
        "hukumonline",
        "hukum online",
        "artikel",
        "berita",
        "website",
        "situs",
        "link",
        "tautan",
        "putusan",
        "pengadilan",
        "terbaru",
        "terkini",
        "hari ini",
        "sumber internet",
        "jurnal",
        "berita terbaru"
    ]

    if any(keyword in q_lower for keyword in external_source_keywords):
        return {
            **state,
            "selected_tools": ["TavilySearch"],
            "reasoning": "Pertanyaan meminta informasi atau sumber eksternal sehingga TavilySearch digunakan.",
            "relevant": True
        }

    # --------------------------------
    # Deteksi pertanyaan lanjutan
    # --------------------------------
    conversation_context = format_conversation_history(history)

    prompt = f"""
Kamu adalah router untuk chatbot KUHP Baru Indonesia.

Tentukan terlebih dahulu apakah pertanyaan pengguna masih berhubungan dengan Kitab Undang-Undang Hukum Pidana (KUHP) Baru.

Jika pertanyaan masih berhubungan dengan KUHP Baru, jangan menolaknya hanya karena membutuhkan sumber eksternal.

Aturan routing:

1. Pertanyaan tentang bunyi/isi pasal:
   gunakan Documents.

2. Pertanyaan yang meminta artikel, berita, website, Hukumonline,
   putusan, sumber internet, informasi terbaru atau sumber eksternal:
   gunakan TavilySearch.

3. Pertanyaan konsep umum KUHP:
   boleh menggunakan Documents dan/atau Wikipedia.

4. Pertanyaan akademik:
   boleh menggunakan Documents dan/atau arXiv.

5. Jika pertanyaan merupakan lanjutan dari percakapan sebelumnya,
   gunakan konteks percakapan untuk memahami maksud pengguna.

6. Hanya anggap pertanyaan di luar domain jika benar-benar tidak
   memiliki hubungan dengan KUHP Baru.

Riwayat percakapan:
{conversation_context}

Pertanyaan:
{q}

Balas tepat dengan format:

TOOLS: Documents
atau
TOOLS: TavilySearch
atau
TOOLS: Wikipedia
atau
TOOLS: arXiv
atau kombinasi yang diperlukan.

REASONING: alasan singkat.
"""

    result = llm.invoke(prompt)
    content = result.content.strip()

    lines = content.split("\n")

    tools_selected = []
    reasoning = ""

    for line in lines:
        line = line.strip()

        if line.startswith("TOOLS:"):
            raw_tools = line.replace("TOOLS:", "").strip()

            for tool_name in [
                "Documents",
                "TavilySearch",
                "Wikipedia",
                "arXiv"
            ]:
                if tool_name in raw_tools:
                    tools_selected.append(tool_name)

        elif line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()

    return {
        **state,
        "selected_tools": tools_selected,
        "reasoning": reasoning,
        "relevant": True
    }

# ================================
# 🔍 Node: Multi Source Retrieval
# ================================
@traceable
def multi_source_retrieve_node(state: AgentState) -> AgentState:
    q = state["question"]
    selected = state.get("selected_tools", [])

    internal_docs = []
    external_docs = []

    article_number = extract_article_number(q)

    # --------------------------------
    # Retrieval dokumen KUHP
    # --------------------------------
    if "Documents" in selected:
        if article_number is not None:
            article = find_article_in_kuhp(article_number)

            if article:
                internal_docs.append(article)
        else:
            # Untuk pertanyaan umum jangan kirim seluruh KUHP
            # karena boros token.
            internal_docs.append(KUHP_TEXT[:30000])

    # --------------------------------
    # Retrieval tools eksternal
    # --------------------------------
    for tool_name in selected:
        if tool_name in tools:
            try:
                result = tools[tool_name].run(q)

                if isinstance(result, list):
                    result_str = ""

                    for i, item in enumerate(result):
                        if isinstance(item, dict):
                            title = item.get("title", "No title")
                            content = item.get("content", "No content")

                            result_str += (
                                f"Result {i+1}: "
                                f"{title} - {content}\n"
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
# 🧮 Node: Grade Relevance
# ================================
@traceable
def enhanced_grade_node(state: AgentState) -> AgentState:
    q = state["question"]

    all_docs = (
        state.get("docs", [])
        + state.get("external_docs", [])
    )

    # --------------------------------
    # Pasal yang ditemukan = relevan
    # --------------------------------
    article_number = extract_article_number(q)

    if article_number is not None:
        article = find_article_in_kuhp(article_number)

        if article:
            return {
                **state,
                "relevant": True
            }

        return {
            **state,
            "relevant": False
        }

    # --------------------------------
    # Jika tidak ada dokumen
    # --------------------------------
    if not all_docs:
        return {
            **state,
            "relevant": False
        }

    prompt = f"""
Evaluasi apakah sumber berikut relevan dengan pertanyaan pengguna.

Pertanyaan:
{q}

Sumber:
{all_docs}

Balas hanya:
ya
atau
tidak
"""

    res = llm.invoke(prompt)

    return {
        **state,
        "relevant": "ya" in res.content.lower()
    }

# ================================
# 🧩 Node: Generate Final Answer
# ================================
@traceable
def enhanced_generation_node(state: AgentState) -> AgentState:
    q = state["question"]

    history = state.get(
        "conversation_history",
        []
    )

    conversation_context = format_conversation_history(
        history
    )

    docs = state.get("docs", [])
    external_docs = state.get(
        "external_docs",
        []
    )

    context = "\n\n".join(
        docs + external_docs
    )

    article_number = extract_article_number(q)

    # --------------------------------
    # PASAL TIDAK DITEMUKAN
    # --------------------------------
    if article_number is not None:
        article = find_article_in_kuhp(article_number)

        if not article:
            return {
                **state,
                "answer": (
                    f"Pasal {article_number} tidak ditemukan "
                    "dalam dokumen KUHP Baru (UU No. 1 Tahun 2023) "
                    "yang digunakan oleh sistem."
                )
            }

    # --------------------------------
    # Tidak ada sumber
    # --------------------------------
    if not context:
        return {
            **state,
            "answer": (
                "Saya tidak menemukan sumber yang cukup "
                "untuk menjawab pertanyaan tersebut."
            )
        }

    prompt = f"""
Kamu adalah asisten hukum khusus Kitab Undang-Undang Hukum Pidana
(KUHP) Baru Indonesia.

ATURAN PALING PENTING:

1. Jangan pernah mengarang fakta hukum.

2. Jangan pernah membuat nomor pasal, bunyi pasal,
   judul artikel, nama putusan, atau sumber yang tidak
   terdapat dalam konteks.

3. Jika pengguna meminta bunyi/isi suatu pasal,
   gunakan HANYA teks pasal yang tersedia dalam konteks.

4. Jika pasal tidak tersedia dalam konteks,
   jangan menebak.

5. Jika pengguna meminta informasi dari situs tertentu
   seperti Hukumonline, gunakan hasil Tavily jika tersedia.
   Jangan mengatakan informasi tidak ditemukan hanya karena
   tidak ada di KUHP_Baru.txt.

6. Gunakan riwayat percakapan untuk memahami kata-kata seperti:
   "di atas", "pasal tersebut", "jelaskan", "yang tadi",
   "itu", dan pertanyaan lanjutan lainnya.

7. Jangan mengulang pertanyaan pengguna.

8. Jangan menambahkan informasi yang tidak didukung sumber.

9. Jawaban harus rapi, formal, dan mudah dibaca.

10. Untuk bunyi pasal, gunakan format:

### Pasal X

(teks pasal)

11. Untuk pertanyaan penjelasan, gunakan paragraf atau
    poin-poin hanya jika memang diperlukan.

12. Jangan menampilkan proses berpikir internal.
    Cukup berikan jawaban dan sumber yang digunakan.

RIWAYAT PERCAKAPAN:
{conversation_context}

PERTANYAAN TERKINI:
{q}

SUMBER INTERNAL KUHP:
{docs}

SUMBER EKSTERNAL:
{external_docs}

Jawablah berdasarkan sumber di atas.
"""

    res = llm.invoke(prompt)

    answer = res.content.strip()

    return {
        **state,
        "answer": answer
    }

# ================================
# 🔁 Node: Answer Check
# ================================
@traceable
def answer_check_node(state: AgentState) -> AgentState:
    q = state["question"]
    ans = state.get("answer", "")

    # Jika jawaban sudah berupa penolakan aman,
    # jangan lakukan retry.
    if (
        "tidak ditemukan" in ans.lower()
        or "tidak menemukan sumber" in ans.lower()
    ):
        return {
            **state,
            "answered": True
        }

    # Jawaban pasal yang ditemukan langsung dianggap selesai.
    article_number = extract_article_number(q)

    if article_number is not None:
        article = find_article_in_kuhp(article_number)

        if article:
            return {
                **state,
                "answered": True
            }

    return {
        **state,
        "answered": bool(ans.strip())
    }

# ================================
# 🔧 Workflow Graph (LangGraph)
# ================================
workflow = StateGraph(AgentState)

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

workflow.set_entry_point(
    "ToolSelection"
)

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

workflow.add_conditional_edges(
    "Evaluate",
    lambda s: "Yes" if s.get("answered") else "No",
    {
        "Yes": END,
        "No": END
    }
)

runnable_graph = workflow.compile()
