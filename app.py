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
    openai_api_key=st.secrets["API_OR"],
    openai_api_base="https://openrouter.ai/api/v1",
    max_tokens=1200
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
# 🔎 DETEKSI NOMOR PASAL
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
# 🔎 DETEKSI UU PDP
# ================================
def mentions_pdp(question):
    q = question.lower()

    pdp_patterns = [
        "uu pdp",
        "uu perlindungan data pribadi",
        "perlindungan data pribadi",
        "undang-undang perlindungan data pribadi",
        "undang undang perlindungan data pribadi",
        "uu no. 27 tahun 2022",
        "uu nomor 27 tahun 2022"
    ]

    return any(pattern in q for pattern in pdp_patterns)

# ================================
# 📚 AMBIL PASAL DARI KUHP_Baru.txt
# ================================
def extract_article(article_number):
    text = kuhp_text

    # Cari awal pasal.
    start_pattern = rf"(?im)^\s*Pasal\s+{article_number}\s*\.?\s*$"
    start_match = re.search(start_pattern, text)

    if not start_match:
        # Fallback jika format dokumen sedikit berbeda.
        start_pattern = rf"(?im)^\s*Pasal\s+{article_number}\s*\.?"
        start_match = re.search(start_pattern, text)

    if not start_match:
        return None

    start = start_match.start()

    # Cari batas akhir pasal.
    # Jangan hanya mencari "Pasal" berikutnya karena
    # struktur UU juga memiliki Bagian, Bab, Paragraf, dll.
    boundary_pattern = (
        r"(?im)^\s*(?:"
        r"Pasal\s+\d+\.?"
        r"|BAB\s+[IVXLCDM0-9]+"
        r"|Bagian\s+(?:Kesatu|Kedua|Ketiga|Keempat|Kelima|Keenam|Ketujuh|Kedelapan|Kesembilan|Kesepuluh|[A-Za-z]+)"
        r"|Paragraf\s+\d+"
        r"|BAB\s+[A-Za-z]+"
        r")\s*$"
    )

    search_start = start_match.end()
    next_boundary = re.search(
        boundary_pattern,
        text[search_start:]
    )

    if next_boundary:
        end = search_start + next_boundary.start()
        article = text[start:end].strip()
    else:
        article = text[start:].strip()

    # Bersihkan baris kosong berlebihan.
    article = re.sub(r"\n{3,}", "\n\n", article)

    return article.strip()

# ================================
# ✨ FORMAT TAMPILAN PASAL
# ================================
def format_article_answer(article_number, article_text):
    """
    Merapikan tampilan pasal tanpa mengubah isi.
    Tidak menggunakan LLM.
    """

    lines = article_text.splitlines()

    cleaned = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Hilangkan titik setelah nomor pasal jika ada.
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
        # Ayat
        if re.match(r"^\(\d+\)", line):
            result += f"{line}\n\n"
        else:
            result += f"{line}\n\n"

    return result.strip()

# ================================
# 🔎 RESOLUSI PERTANYAAN KONTEKSTUAL
# ================================
def resolve_contextual_question(question, history):
    q = question.strip().lower()

    contextual_patterns = [
        "pasal di atas",
        "pasal tersebut",
        "pasal tadi",
        "pasal itu",
        "ketentuan di atas",
        "ketentuan tersebut",
        "ketentuan tadi",
        "aturan di atas",
        "aturan tersebut",
        "aturan tadi",
        "hal di atas",
        "hal tersebut",
        "hal tadi",
        "jelaskan di atas",
        "jelaskan hal di atas",
        "jelaskan ketentuan di atas",
        "jelaskan pasal di atas"
    ]

    if not any(pattern in q for pattern in contextual_patterns):
        return question

    if not history:
        return question

    # Cari percakapan sebelumnya dari belakang.
    for msg in reversed(history):
        role = msg.get("role", "")

        if role != "user":
            continue

        previous_question = msg.get("text", "").strip()

        if not previous_question:
            continue

        article_number = detect_article_number(previous_question)

        if article_number is not None:
            return (
                f"{question}\n\n"
                f"[KONTEKS INTERNAL: Pengguna sedang merujuk "
                f"pada Pasal {article_number} KUHP Baru.]"
            )

    return question

# ================================
# 🧠 NODE: VALIDASI
# ================================
@traceable
def validation_node(state: AgentState) -> AgentState:
    original_question = state["question"]
    history = state.get("conversation_history", [])

    q = resolve_contextual_question(
        original_question,
        history
    )

    article_number = detect_article_number(q)

    # --------------------------------
    # UU PDP -> TOLAK
    # --------------------------------
    if mentions_pdp(q):
        return {
            **state,
            "question": q,
            "article_number": article_number,
            "direct_article": False,
            "relevant": False,
            "answer": (
                "saya tidak bisa menjawab pertanyaan Anda karena "
                "tidak berkaitan dengan Kitab Undang-Undang Hukum Pidana "
                "(KUHP) baru"
            ),
            "reasoning": (
                "Pertanyaan merujuk pada UU Perlindungan Data Pribadi, "
                "bukan KUHP Baru."
            )
        }

    # --------------------------------
    # PERTANYAAN PASAL
    # --------------------------------
    if article_number is not None:

        article_text = extract_article(article_number)

        # PASAL TIDAK ADA
        if article_text is None:
            return {
                **state,
                "question": q,
                "article_number": article_number,
                "article_text": None,
                "direct_article": True,
                "relevant": False,
                "answer": (
                    f"### Pasal {article_number}\n\n"
                    f"Pasal {article_number} tidak ditemukan dalam "
                    f"dokumen **KUHP_Baru.txt** yang digunakan oleh sistem."
                ),
                "reasoning": (
                    f"Pasal {article_number} tidak ditemukan secara "
                    f"langsung dalam KUHP_Baru.txt. Sistem tidak "
                    f"menggunakan LLM untuk mengarang isi pasal."
                )
            }

        # PASAL ADA
        return {
            **state,
            "question": q,
            "article_number": article_number,
            "article_text": article_text,
            "direct_article": True,
            "relevant": True,
            "reasoning": (
                f"Pasal {article_number} ditemukan langsung "
                f"dalam KUHP_Baru.txt."
            )
        }

    # --------------------------------
    # PERTANYAAN UMUM
    # --------------------------------
    return {
        **state,
        "question": q,
        "article_number": None,
        "direct_article": False
    }

# ================================
# 🧠 NODE: TOOL SELECTION
# ================================
@traceable
def tool_selection_node(state: AgentState) -> AgentState:

    # Pasal tidak boleh masuk tool selection.
    if state.get("direct_article"):
        return {
            **state,
            "selected_tools": [],
            "reasoning": state.get(
                "reasoning",
                "Pertanyaan pasal diproses langsung dari KUHP_Baru.txt."
            )
        }

    # Jika sudah ditolak.
    if state.get("answer"):
        return {
            **state,
            "selected_tools": []
        }

    q = state["question"]

    prompt = f"""
Kamu adalah router untuk chatbot Kitab Undang-Undang Hukum Pidana
(KUHP) Baru Indonesia.

Tentukan apakah pertanyaan berikut berkaitan dengan KUHP Baru.

Pertanyaan:
{q}

Jika tidak berkaitan dengan KUHP Baru, jawab:
TOOLS: NONE
REASONING: OUT_OF_SCOPE

Jika berkaitan dengan KUHP Baru, pilih maksimal SATU tools eksternal
jika benar-benar diperlukan.

Tools:
Wikipedia
arXiv
TavilySearch

Aturan:
- Wikipedia untuk konsep umum.
- arXiv untuk penelitian akademik.
- TavilySearch untuk informasi terbaru.
- Jika pertanyaan dapat dijawab dari KUHP_Baru.txt,
  jangan pilih tools eksternal.
- Jangan memilih lebih dari satu tool.

Format:
TOOLS: nama_tool
REASONING: alasan
"""

    result = llm.invoke(prompt)
    content = result.content.strip()

    tools_selected = []
    reasoning = ""

    for line in content.split("\n"):
        line = line.strip()

        if line.startswith("TOOLS:"):
            selected = line.replace("TOOLS:", "").strip()

            if selected and selected.upper() != "NONE":
                if selected in tools:
                    tools_selected = [selected]

        elif line.startswith("REASONING:"):
            reasoning = line.replace(
                "REASONING:",
                ""
            ).strip()

    if "OUT_OF_SCOPE" in content:
        return {
            **state,
            "selected_tools": [],
            "relevant": False,
            "answer": (
                "saya tidak bisa menjawab pertanyaan Anda karena "
                "tidak berkaitan dengan Kitab Undang-Undang Hukum Pidana "
                "(KUHP) baru"
            ),
            "reasoning": (
                "Pertanyaan berada di luar cakupan KUHP Baru."
            )
        }

    return {
        **state,
        "selected_tools": tools_selected,
        "reasoning": reasoning
    }

# ================================
# 🔍 NODE: RETRIEVAL
# ================================
@traceable
def multi_source_retrieve_node(state: AgentState) -> AgentState:

    # --------------------------------
    # PASAL -> LANGSUNG DOKUMEN
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
    # OUT OF SCOPE
    # --------------------------------
    if state.get("answer"):
        return {
            **state,
            "docs": [],
            "external_docs": []
        }

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
    # PASAL TIDAK DITEMUKAN
    # --------------------------------
    if state.get("direct_article") and not state.get("article_text"):
        return state

    # --------------------------------
    # PASAL DITEMUKAN
    # --------------------------------
    if state.get("direct_article"):

        article_number = state.get("article_number")
        article_text = state.get("article_text")
        q = state["question"].lower()

        # Jika meminta bunyi / isi pasal,
        # TIDAK PERLU LLM.
        direct_patterns = [
            "apa bunyi",
            "apa isi",
            "bunyi pasal",
            "isi pasal",
            "tuliskan pasal",
            "tuliskan isi",
            "sebutkan pasal",
            "kutip pasal",
            "tampilkan pasal"
        ]

        if any(pattern in q for pattern in direct_patterns):
            return {
                **state,
                "answer": format_article_answer(
                    article_number,
                    article_text
                )
            }

        # --------------------------------
        # PENJELASAN PASAL
        # --------------------------------
        history = format_conversation_history(
            state.get("conversation_history", [])
        )

        prompt = f"""
Kamu adalah asisten yang menjelaskan Kitab Undang-Undang
Hukum Pidana (KUHP) Baru Indonesia.

Pengguna meminta penjelasan mengenai Pasal {article_number}.

ATURAN SANGAT KETAT:

1. Satu-satunya dasar untuk menjelaskan Pasal {article_number}
   adalah teks pasal yang diberikan di bawah.
2. Jangan mengarang.
3. Jangan membuat ayat, angka, sanksi, unsur pidana,
   pengecualian, atau ketentuan yang tidak ada dalam teks.
4. Jangan menggunakan pengetahuan internal model untuk
   menggantikan informasi yang tidak terdapat dalam teks.
5. Jika suatu informasi tidak terdapat dalam teks pasal,
   katakan bahwa informasi tersebut tidak terdapat dalam
   teks pasal.
6. Jangan mencampurkan Pasal {article_number} dengan pasal lain.
7. Jika konteks percakapan menyebut "pasal di atas",
   konteks tersebut merujuk pada Pasal {article_number}.
8. Gunakan bahasa Indonesia yang rapi dan mudah dipahami.

RIWAYAT PERCAKAPAN:
{history}

TEKS PASAL {article_number}:
{article_text}

PERTANYAAN:
{state["question"]}

Format jawaban:

### Penjelasan Pasal {article_number}

**Inti ketentuan:**
Jelaskan secara singkat berdasarkan teks.

**Penjelasan:**
Jelaskan setiap ketentuan/ayat secara berurutan jika ada.

**Catatan:**
Sampaikan batasan informasi jika memang diperlukan.

Jangan menambahkan informasi hukum yang tidak terdapat
dalam teks pasal.
"""

        res = llm.invoke(prompt)

        return {
            **state,
            "answer": res.content.strip()
        }

    # --------------------------------
    # OUT OF SCOPE
    # --------------------------------
    if state.get("answer"):
        return state

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

ATURAN WAJIB:

1. Jawab hanya jika pertanyaan berkaitan dengan KUHP Baru.
2. Utamakan KUHP_Baru.txt.
3. Jangan mengarang isi hukum.
4. Jangan membuat nomor pasal yang tidak ada.
5. Jangan mengarang bunyi pasal.
6. Jika informasi tidak ditemukan dalam sumber,
   katakan bahwa informasi tersebut tidak ditemukan.
7. Jangan menggunakan pengetahuan internal model untuk
   menggantikan informasi yang tidak tersedia.
8. Gunakan conversation history untuk memahami pertanyaan
   lanjutan.
9. Jangan menganggap pertanyaan lanjutan sebagai pertanyaan
   yang berdiri sendiri jika konteks sebelumnya jelas.

RIWAYAT PERCAKAPAN:
{history}

PERTANYAAN:
{q}

SUMBER:
{context}

Jawab dengan bahasa Indonesia formal, rapi, jelas,
dan tidak bertele-tele.
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

workflow.add_conditional_edges(
    "Validation",
    lambda s: (
        "DirectAnswer"
        if s.get("direct_article")
        else (
            "OutOfScope"
            if s.get("answer")
            else "ToolSelection"
        )
    ),
    {
        "DirectAnswer": "Retrieve",
        "OutOfScope": END,
        "ToolSelection": "ToolSelection"
    }
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
