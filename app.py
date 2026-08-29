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
# 🧠 Memori Percakapan
# ================================
if "conversation_memory" not in st.session_state:
    st.session_state.conversation_memory = []

def format_conversation_history(history, max_turns=6):
    if not history:
        return "Belum ada percakapan sebelumnya."

    recent = history[-max_turns:]
    formatted = []

    for item in recent:
        role = item.get("role", "")
        text = item.get("text", "")

        if role == "user":
            formatted.append(f"Pengguna: {text}")
        elif role in ["assistant", "Asisten"]:
            formatted.append(f"Asisten: {text}")

    return "\n".join(formatted)

# ================================
# 📚 Load Dokumen KUHP Baru
# ================================
with open("KUHP_Baru.txt", "r", encoding="utf-8") as f:
    kuhp_text = f.read()

documents = [kuhp_text]

# ================================
# 🔎 Extract Pasal dari KUHP
# ================================
def get_article_number(question):
    """
    Mendeteksi nomor pasal yang ditanyakan.
    Contoh:
    - apa bunyi pasal 333?
    - jelaskan Pasal 333 KUHP
    - pasal 3
    """
    match = re.search(
        r"\bpasal\s+(\d+[A-Za-z]?)\b",
        question,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return None

def get_article_from_document(article_number):
    """
    Mengambil bagian pasal tertentu dari KUHP_Baru.txt
    sehingga seluruh dokumen tidak dikirim ke LLM.
    """

    if not article_number:
        return None

    pattern = re.compile(
        rf"(?im)^\s*Pasal\s+{re.escape(str(article_number))}\b.*?(?=^\s*Pasal\s+\d+[A-Za-z]?\b|\Z)",
        re.DOTALL
    )

    match = pattern.search(kuhp_text)

    if match:
        return match.group(0).strip()

    return None

# ================================
# 🔍 Deteksi Jenis Pertanyaan
# ================================
def is_explicitly_not_kuhp(question):
    q = question.lower()

    pdp_patterns = [
        "uu pdp",
        "uu no. 27 tahun 2022",
        "uu nomor 27 tahun 2022",
        "perlindungan data pribadi",
        "undang-undang perlindungan data pribadi",
        "pelindungan data pribadi"
    ]

    for pattern in pdp_patterns:
        if pattern in q:
            return True

    return False

def is_kuhp_related(question):
    """
    Filter awal untuk menghemat token.
    Tidak menggunakan LLM.
    """

    q = question.lower()

    # Jika secara eksplisit menyebut UU PDP,
    # jangan dianggap sebagai pertanyaan KUHP.
    if is_explicitly_not_kuhp(q):
        return False

    kuhp_keywords = [
        "kuhp",
        "pidana",
        "hukum pidana",
        "tindak pidana",
        "kejahatan",
        "pelanggaran",
        "hukuman",
        "pidana penjara",
        "pidana denda",
        "pemidanaan",
        "delik",
        "tersangka",
        "terdakwa",
        "perampasan",
        "pembunuhan",
        "pencurian",
        "penganiayaan",
        "pemerkosaan",
        "pencabulan",
        "penipuan",
        "penggelapan",
        "korupsi",
        "suap",
        "penyiksaan",
        "penghinaan",
        "pencemaran",
        "pasal"
    ]

    return any(keyword in q for keyword in kuhp_keywords)

# ================================
# 🧩 Define Agent State
# ================================
class AgentState(TypedDict):
    question: str
    docs: Optional[List[str]]
    external_docs: Optional[List[str]]
    answer: Optional[str]
    relevant: Optional[bool]
    answered: Optional[bool]
    selected_tools: Optional[List[str]]
    reasoning: Optional[str]
    conversation_history: Optional[List[dict]]
    article_number: Optional[str]
    article_text: Optional[str]
    out_of_scope: Optional[bool]

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
        description="Gunakan untuk menemukan konsep utama, sejarah, dan hal-hal lain yang berkaitan dengan Kitab Undang-Undang Hukum Pidana (KUHP) baru dalam Bahasa Indonesia!"
    ),
    "arXiv": Tool(
        name="arXiv",
        func=arxiv_tool.run,
        description="Gunakan untuk referensi akademik tentang teori atau penelitian berkaitan Kitab Undang-Undang Hukum Pidana (KUHP) baru!"
    ),
    "TavilySearch": Tool(
        name="TavilySearch",
        func=tavily_tool_instance.run,
        description="Gunakan untuk menemukan berita, peraturan Indonesia, atau putusan pengadilan, maupun direktori/repositori pengadilan mengenai penggunaan Kitab Undang-Undang Hukum Pidana (KUHP) baru."
    )
}

# ================================
# 🧠 Node: Tool Selection
# ================================
@traceable
def tool_selection_node(state: AgentState) -> AgentState:
    q = state["question"]

    article_number = get_article_number(q)
    article_text = get_article_from_document(article_number)

    # --------------------------------
    # Tolak pertanyaan yang jelas bukan KUHP
    # --------------------------------
    if not is_kuhp_related(q):
        return {
            **state,
            "selected_tools": [],
            "reasoning": "Pertanyaan berada di luar cakupan KUHP Baru.",
            "out_of_scope": True,
            "article_number": article_number,
            "article_text": article_text
        }

    # --------------------------------
    # Pertanyaan pasal → langsung dokumen
    # --------------------------------
    if article_number:
        if article_text:
            return {
                **state,
                "selected_tools": [],
                "reasoning": f"Pertanyaan meminta Pasal {article_number}. Sistem mengambil langsung Pasal {article_number} dari KUHP_Baru.txt.",
                "article_number": article_number,
                "article_text": article_text,
                "out_of_scope": False
            }

        return {
            **state,
            "selected_tools": [],
            "reasoning": f"Pasal {article_number} tidak ditemukan dalam KUHP_Baru.txt.",
            "article_number": article_number,
            "article_text": None,
            "out_of_scope": False
        }

    # --------------------------------
    # Untuk pertanyaan lanjutan seperti
    # "jelaskan pasal di atas"
    # --------------------------------
    history = state.get("conversation_history", [])
    conversation_context = format_conversation_history(history)

    prompt = f"""
Kamu adalah router untuk chatbot KUHP Baru Indonesia.

Tentukan sumber yang diperlukan untuk pertanyaan pengguna.

Percakapan sebelumnya:
{conversation_context}

Pertanyaan sekarang:
{q}

Pilihan:
1. Wikipedia
2. arXiv
3. TavilySearch
4. Documents

Aturan:
- Jika membutuhkan isi atau penjelasan pasal KUHP → Documents.
- Jika membutuhkan informasi terbaru → TavilySearch.
- Jika membutuhkan teori akademik → arXiv.
- Jika membutuhkan konsep umum → Wikipedia.
- Jika pertanyaan merupakan lanjutan dari pembahasan sebelumnya, gunakan konteks percakapan.
- Jangan memilih semua tools.
- Pilih maksimal 2 tools.

Format:
TOOLS: tool1,tool2
REASONING: alasan singkat
"""

    result = llm.invoke(prompt)

    lines = result.content.strip().split("\n")
    tools_selected = []
    reasoning = ""

    for line in lines:
        if line.startswith("TOOLS:"):
            tools_selected = [
                t.strip()
                for t in line.replace("TOOLS:", "").split(",")
                if t.strip() in tools
            ]

        elif line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()

    return {
        **state,
        "selected_tools": tools_selected,
        "reasoning": reasoning,
        "article_number": article_number,
        "article_text": article_text,
        "out_of_scope": False
    }

# ================================
# 🔍 Node: Multi Source Retrieval
# ================================
@traceable
def multi_source_retrieve_node(state: AgentState) -> AgentState:
    q = state["question"]

    # --------------------------------
    # Pertanyaan di luar KUHP
    # --------------------------------
    if state.get("out_of_scope"):
        return {
            **state,
            "docs": [],
            "external_docs": []
        }

    article_text = state.get("article_text")
    selected = state.get("selected_tools", [])

    # --------------------------------
    # Jika pasal ditemukan:
    # jangan panggil tools eksternal
    # --------------------------------
    if article_text:
        return {
            **state,
            "docs": [article_text],
            "external_docs": []
        }

    # --------------------------------
    # Retrieval normal
    # --------------------------------
    internal_docs = []
    external_docs = []

    # Jangan mengirim seluruh KUHP jika
    # tidak diperlukan.
    if "Documents" in selected:
        internal_docs = documents

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
                            result_str += f"Result {i+1}: {str(item)}\n"

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
    # Tidak perlu grading untuk pasal
    # yang sudah ditemukan secara langsung.
    if state.get("article_text"):
        return {
            **state,
            "relevant": True
        }

    if state.get("out_of_scope"):
        return {
            **state,
            "relevant": False
        }

    q = state["question"]

    all_docs = (
        state.get("docs", []) +
        state.get("external_docs", [])
    )

    # Batasi context agar tidak boros token.
    context = "\n".join(all_docs)

    if len(context) > 18000:
        context = context[:18000]

    prompt = f"""
Evaluasi apakah sumber berikut relevan untuk pertanyaan tentang KUHP Baru.

Pertanyaan:
{q}

Sumber:
{context}

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

    # --------------------------------
    # Jawaban untuk pertanyaan di luar KUHP
    # --------------------------------
    if state.get("out_of_scope"):
        answer = (
            "saya tidak bisa menjawab pertanyaan Anda karena "
            "tidak berkaitan dengan Kitab Undang-Undang Hukum "
            "Pidana (KUHP) baru"
        )

        return {
            **state,
            "answer": answer
        }

    # --------------------------------
    # Jika pertanyaan pasal dan ditemukan
    # --------------------------------
    article_number = state.get("article_number")
    article_text = state.get("article_text")

    if article_text:
        history = state.get("conversation_history", [])
        conversation_context = format_conversation_history(history)

        prompt = f"""
Kamu adalah asisten ahli Kitab Undang-Undang Hukum Pidana (KUHP) Baru Indonesia.

Pertanyaan pengguna:
{q}

Pasal yang ditemukan secara langsung dari dokumen KUHP Baru:
{article_text}

Percakapan sebelumnya:
{conversation_context}

Aturan:
- Gunakan isi pasal di atas sebagai sumber utama.
- Jangan mengganti isi pasal dengan KUHP lama.
- Jangan mengarang nomor atau isi pasal.
- Jika pengguna meminta "bunyi pasal", tampilkan bunyi pasal tersebut.
- Jika pengguna meminta penjelasan, jelaskan berdasarkan pasal tersebut.
- Jika pengguna mengatakan "pasal di atas", gunakan konteks percakapan sebelumnya.
- Gunakan bahasa Indonesia formal tetapi mudah dipahami.
"""

        res = llm.invoke(prompt)

        return {
            **state,
            "answer": res.content.strip()
        }

    # --------------------------------
    # Pertanyaan umum KUHP
    # --------------------------------
    history = state.get("conversation_history", [])
    conversation_context = format_conversation_history(history)

    context = "\n".join(
        state.get("docs", []) +
        state.get("external_docs", [])
    )

    if len(context) > 18000:
        context = context[:18000]

    prompt = f"""
Kamu adalah asisten ahli Kitab Undang-Undang Hukum Pidana (KUHP) Baru di Indonesia.

Percakapan sebelumnya:
{conversation_context}

Pertanyaan pengguna:
{q}

Konteks sumber:
{context}

Aturan:
1. Jawab hanya mengenai KUHP Baru.
2. Gunakan percakapan sebelumnya jika pertanyaan merupakan pertanyaan lanjutan.
3. Utamakan dokumen KUHP Baru.
4. Jangan mengarang pasal.
5. Jangan mencampurkan KUHP lama dengan KUHP Baru.
6. Jika sumber tidak cukup, katakan dengan jujur bahwa informasi belum ditemukan.
7. Jawab secara ringkas tetapi substantif.
8. Sebutkan sumber yang digunakan.

Jawaban dalam bahasa Indonesia formal.
"""

    res = llm.invoke(prompt)

    return {
        **state,
        "answer": res.content.strip()
    }

# ================================
# 🔁 Node: Answer Check
# ================================
@traceable
def answer_check_node(state: AgentState) -> AgentState:
    # Tidak perlu LLM kedua untuk validasi.
    # Ini menghemat token dan waktu.
    answer = state.get("answer", "")

    return {
        **state,
        "answered": bool(answer.strip())
    }

# ================================
# 🔧 Workflow Graph
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

workflow.set_entry_point("ToolSelection")

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

workflow.add_edge(
    "Evaluate",
    END
)

runnable_graph = workflow.compile()
