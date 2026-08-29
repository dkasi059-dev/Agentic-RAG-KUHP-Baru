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

tavily_tool_instance = TavilySearch(
    max_results=3
)

tools = {
    "Wikipedia": Tool(
        name="Wikipedia",
        func=wikipedia_tool.run,
        description="Gunakan untuk konsep umum yang berkaitan dengan KUHP Baru."
    ),
    "arXiv": Tool(
        name="arXiv",
        func=arxiv_tool.run,
        description="Gunakan untuk penelitian akademik yang berkaitan dengan KUHP Baru."
    ),
    "TavilySearch": Tool(
        name="TavilySearch",
        func=tavily_tool_instance.run,
        description="Gunakan untuk informasi terbaru, peraturan Indonesia, berita hukum, dan putusan pengadilan."
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

    # Batasi memory agar tidak boros token.
    # Hanya 8 pesan terakhir.
    for msg in history[-8:]:
        role = msg.get("role", "")
        text = msg.get("text", "")

        if role == "user":
            formatted.append(f"Pengguna: {text}")
        elif role in ["assistant", "Asisten"]:
            formatted.append(f"Asisten: {text}")

    return "\n".join(formatted)

# ================================
# 🔎 DETEKSI PASAL
# ================================
def detect_article_number(question):
    """
    Mendeteksi pola:
    - pasal 333
    - Pasal 333 KUHP
    - pasal ke-333
    """

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
# 🔎 CEK APAKAH MENYEBUT UU PDP
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
# 🔎 AMBIL PASAL SECARA DETERMINISTIK
# ================================
def extract_article(article_number):
    """
    Mengambil isi pasal LANGSUNG dari KUHP_Baru.txt.

    Tidak menggunakan LLM.
    Tidak menggunakan Tavily.
    Tidak menggunakan Wikipedia.
    Tidak menggunakan arXiv.

    Jika pasal tidak ditemukan -> None.
    """

    text = kuhp_text

    # Variasi format:
    # Pasal 333
    # Pasal 333.
    # PASAL 333
    pattern = rf"(?im)^\s*pasal\s+{article_number}\s*\.?\s*$"

    match = re.search(pattern, text)

    if not match:
        # Beberapa dokumen memiliki teks seperti:
        # Pasal 333
        # (1) ...
        # sehingga coba pola yang lebih fleksibel.
        pattern = rf"(?im)^\s*pasal\s+{article_number}\s*\.?\s*(?:\n|$)"
        match = re.search(pattern, text)

    if not match:
        return None

    start = match.start()

    # Cari Pasal berikutnya.
    next_pattern = r"(?im)^\s*pasal\s+\d+\s*\.?\s*$"
    next_matches = list(re.finditer(next_pattern, text[match.end():]))

    if next_matches:
        end = match.end() + next_matches[0].start()
        article = text[start:end].strip()
    else:
        article = text[start:].strip()

    return article

# ================================
# 🔎 RESOLUSI "PASAL DI ATAS"
# ================================
def resolve_contextual_question(question, history):
    """
    Menangani pertanyaan seperti:
    - jelaskan pasal di atas
    - jelaskan pasal tersebut
    - bagaimana penerapannya?
    - apa maksud pasal tadi?

    Menggunakan conversation history.
    """

    q = question.lower()

    contextual_patterns = [
        "pasal di atas",
        "pasal tersebut",
        "pasal tadi",
        "pasal itu",
        "ketentuan di atas",
        "ketentuan tersebut",
        "aturan di atas",
        "aturan tersebut"
    ]

    if not any(pattern in q for pattern in contextual_patterns):
        return question

    if not history:
        return question

    # Cari pesan user sebelumnya yang mengandung nomor pasal.
    for msg in reversed(history):
        if msg.get("role") == "user":
            previous_question = msg.get("text", "")
            article_number = detect_article_number(previous_question)

            if article_number is not None:
                return f"{question}\n\nKonteks pasal yang dirujuk adalah Pasal {article_number} KUHP Baru."

    return question

# ================================
# 🧠 NODE: VALIDASI AWAL
# ================================
@traceable
def validation_node(state: AgentState) -> AgentState:
    original_question = state["question"]
    history = state.get("conversation_history", [])

    # Resolusi konteks percakapan.
    q = resolve_contextual_question(
        original_question,
        history
    )

    article_number = detect_article_number(q)

    # --------------------------------
    # Kasus eksplisit UU PDP
    # --------------------------------
    if mentions_pdp(q):
        return {
            **state,
            "question": q,
            "article_number": article_number,
            "direct_article": False,
            "relevant": False,
            "reasoning": "Pertanyaan merujuk pada UU Perlindungan Data Pribadi, bukan KUHP Baru.",
            "answer": "saya tidak bisa menjawab pertanyaan Anda karena tidak berkaitan dengan Kitab Undang-Undang Hukum Pidana (KUHP) baru"
        }

    # --------------------------------
    # Kasus pertanyaan pasal
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
                    f"Pasal {article_number} tidak ditemukan dalam dokumen "
                    f"KUHP Baru (KUHP_Baru.txt) yang digunakan oleh sistem."
                ),
                "reasoning": (
                    f"Pasal {article_number} tidak ditemukan secara literal "
                    "di dokumen KUHP_Baru.txt. Sistem tidak menggunakan "
                    "LLM atau sumber eksternal untuk mengarang isi pasal."
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
                f"Pasal {article_number} ditemukan langsung di "
                "KUHP_Baru.txt."
            )
        }

    # --------------------------------
    # Pertanyaan umum
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
    # Jangan pernah memanggil LLM untuk pasal.
    if state.get("direct_article"):
        return {
            **state,
            "selected_tools": [],
            "reasoning": state.get(
                "reasoning",
                "Pertanyaan pasal diproses langsung dari KUHP_Baru.txt."
            )
        }

    q = state["question"]

    prompt = f"""
Kamu adalah router untuk chatbot KUHP Baru Indonesia.

Tentukan apakah pertanyaan berikut berkaitan dengan KUHP Baru.

Pertanyaan:
{q}

Jika tidak berkaitan dengan KUHP Baru, jawab:
TOOLS: NONE
REASONING: OUT_OF_SCOPE

Jika berkaitan, pilih maksimal SATU tools eksternal jika benar-benar diperlukan.

Pilihan:
Wikipedia
arXiv
TavilySearch

Gunakan:
- Wikipedia untuk konsep umum.
- arXiv untuk penelitian akademik.
- TavilySearch untuk informasi terbaru.

Jika pertanyaan dapat dijawab menggunakan KUHP_Baru.txt,
jangan pilih tools eksternal.

Format wajib:
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
            reasoning = line.replace("REASONING:", "").strip()

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
            "reasoning": "Pertanyaan berada di luar cakupan KUHP Baru."
        }

    return {
        **state,
        "selected_tools": tools_selected,
        "reasoning": reasoning
    }

# ================================
# 🔍 NODE: MULTI SOURCE RETRIEVAL
# ================================
@traceable
def multi_source_retrieve_node(state: AgentState) -> AgentState:

    # --------------------------------
    # PASAL -> LANGSUNG DARI DOKUMEN
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

    # Dokumen KUHP tetap menjadi sumber utama.
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

        # Jika hanya meminta bunyi/isi pasal,
        # JANGAN gunakan LLM.
        direct_patterns = [
            "apa bunyi",
            "apa isi",
            "bunyi pasal",
            "isi pasal",
            "tuliskan pasal",
            "tuliskan isi",
            "sebutkan pasal",
            "apa yang dimaksud pasal"
        ]

        if any(pattern in q for pattern in direct_patterns):
            return {
                **state,
                "answer": article_text
            }

        # Jika meminta penjelasan,
        # LLM hanya boleh menjelaskan teks yang sudah ditemukan.
        history = format_conversation_history(
            state.get("conversation_history", [])
        )

        prompt = f"""
Kamu adalah asisten hukum yang menjelaskan KUHP Baru Indonesia.

ATURAN SANGAT KETAT:

1. Satu-satunya sumber utama untuk Pasal {article_number}
   adalah teks pasal di bawah ini.
2. Jangan mengubah bunyi pasal.
3. Jangan membuat ayat, angka, hukuman, unsur pidana,
   pengecualian, atau istilah yang tidak terdapat dalam teks.
4. Jangan menggunakan pengetahuan dari luar teks untuk
   mengisi kekosongan.
5. Jika informasi tidak terdapat dalam teks pasal,
   katakan bahwa informasi tersebut tidak terdapat dalam
   teks pasal yang tersedia.
6. Jangan pernah mengarang isi pasal.
7. Bedakan dengan jelas antara KUTIPAN PASAL dan PENJELASAN.
8. Jika pengguna mengatakan "pasal di atas", gunakan konteks
   percakapan yang diberikan.

Konteks percakapan:
{history}

Teks resmi yang ditemukan dalam KUHP_Baru.txt:

{article_text}

Pertanyaan pengguna:
{state["question"]}

Berikan jawaban berdasarkan teks tersebut.
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
8. Gunakan conversation history untuk memahami konteks
   pertanyaan lanjutan.
9. Jangan menganggap pertanyaan baru berdiri sendiri jika
   konteks sebelumnya jelas masih berhubungan.

RIWAYAT PERCAKAPAN:
{history}

PERTANYAAN:
{q}

SUMBER:
{context}

Jawab dengan bahasa Indonesia formal, jelas, dan ringkas.
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
