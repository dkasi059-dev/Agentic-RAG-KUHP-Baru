import os
import re
import json
import streamlit as st
from typing import TypedDict, List, Optional, Literal

from langchain_core.tools import Tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_tavily import TavilySearch

from langgraph.graph import StateGraph, END
from langsmith import traceable
from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field


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
        description=(
            "Gunakan ketika diperlukan informasi konseptual atau "
            "pengetahuan umum yang membantu menjawab pertanyaan."
        )
    ),

    "arXiv": Tool(
        name="arXiv",
        func=arxiv_tool.run,
        description=(
            "Gunakan ketika diperlukan penelitian atau literatur "
            "akademik yang relevan."
        )
    ),

    "TavilySearch": Tool(
        name="TavilySearch",
        func=tavily_tool_instance.run,
        description=(
            "Gunakan ketika diperlukan informasi eksternal yang "
            "terkini, sumber web, regulasi, berita, putusan, atau "
            "informasi lain yang perlu dicari di internet."
        )
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
            formatted.append(
                f"Pengguna: {text}"
            )

        elif role in ["assistant", "Asisten"]:
            formatted.append(
                f"Asisten: {text}"
            )

    if not formatted:
        return "Tidak ada percakapan sebelumnya."

    return "\n".join(formatted)


# ================================
# 📚 AMBIL PASAL DARI KUHP_Baru.txt
# ================================
def extract_article(article_number):

    text = kuhp_text

    # Cari awal pasal.
    start_pattern = (
        rf"(?im)^\s*Pasal\s+"
        rf"{article_number}"
        rf"\s*\.?\s*$"
    )

    start_match = re.search(
        start_pattern,
        text
    )

    if not start_match:

        # Fallback jika format dokumen sedikit berbeda.
        start_pattern = (
            rf"(?im)^\s*Pasal\s+"
            rf"{article_number}"
            rf"\s*\.?"
        )

        start_match = re.search(
            start_pattern,
            text
        )

    if not start_match:
        return None

    start = start_match.start()

    # Cari batas akhir pasal.
    boundary_pattern = (
        r"(?im)^\s*(?:"
        r"Pasal\s+\d+\.?"
        r"|BAB\s+[IVXLCDM0-9]+"
        r"|Bagian\s+(?:Kesatu|Kedua|Ketiga|Keempat|Kelima|"
        r"Keenam|Ketujuh|Kedelapan|Kesembilan|Kesepuluh|[A-Za-z]+)"
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

        end = (
            search_start +
            next_boundary.start()
        )

        article = text[start:end].strip()

    else:

        article = text[start:].strip()

    # Bersihkan baris kosong berlebihan.
    article = re.sub(
        r"\n{3,}",
        "\n\n",
        article
    )

    return article.strip()


# ================================
# ✨ FORMAT TAMPILAN PASAL
# ================================
def format_article_answer(
    article_number,
    article_text
):

    lines = article_text.splitlines()

    cleaned = []

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Hilangkan heading Pasal.
        if re.fullmatch(
            rf"Pasal\s+{article_number}\.?",
            line,
            re.IGNORECASE
        ):
            continue

        cleaned.append(line)

    if not cleaned:

        return (
            f"### Pasal {article_number}\n\n"
            f"Teks pasal tidak tersedia."
        )

    result = (
        f"### Pasal {article_number}\n\n"
    )

    for line in cleaned:

        if re.match(
            r"^\(\d+\)",
            line
        ):
            result += f"{line}\n\n"

        else:
            result += f"{line}\n\n"

    return result.strip()


# ================================
# 🔎 RESOLUSI PERTANYAAN KONTEKSTUAL
# ================================
def resolve_contextual_question(
    question,
    history
):

    if not history:
        return question

    history_text = format_conversation_history(
        history
    )

    # Tidak menggunakan daftar keyword.
    # LLM menentukan apakah pertanyaan merupakan
    # kelanjutan dari konteks sebelumnya.

    class ContextResolution(BaseModel):

        is_contextual: bool = Field(
            description=(
                "Apakah pertanyaan pengguna merupakan "
                "kelanjutan dari percakapan sebelumnya?"
            )
        )

        resolved_question: str = Field(
            description=(
                "Pertanyaan yang telah dipahami berdasarkan "
                "konteks percakapan sebelumnya. Jika tidak "
                "memerlukan konteks, pertahankan pertanyaan "
                "aslinya."
            )
        )

    resolver = llm.with_structured_output(
        ContextResolution
    )

    prompt = f"""
Anda bertugas memahami konteks percakapan.

Jangan menggunakan daftar keyword atau aturan berbasis
pencocokan kata.

Gunakan kemampuan penalaran bahasa Anda untuk menentukan
apakah pertanyaan terbaru bergantung pada percakapan
sebelumnya.

Jika memang bergantung pada konteks sebelumnya, ubah
pertanyaan menjadi bentuk yang lebih lengkap sehingga
dapat dipahami tanpa kehilangan maksud pengguna.

Jika tidak bergantung pada konteks sebelumnya,
pertahankan pertanyaan tersebut.

RIWAYAT:
{history_text}

PERTANYAAN TERBARU:
{question}
"""

    try:

        result = resolver.invoke(prompt)

        return result.resolved_question.strip()

    except Exception:

        return question


# ================================
# 🧠 SCHEMA ROUTER
# ================================
class RouterDecision(BaseModel):

    relevant: bool = Field(
        description=(
            "Apakah pertanyaan pengguna berkaitan secara "
            "substantif dengan KUHP Baru Indonesia?"
        )
    )

    article_number: Optional[int] = Field(
        default=None,
        description=(
            "Nomor pasal KUHP Baru yang menjadi fokus "
            "pertanyaan jika dapat diidentifikasi. "
            "Gunakan null jika tidak ada atau tidak diperlukan."
        )
    )

    direct_article: bool = Field(
        description=(
            "Apakah pertanyaan membutuhkan pengambilan "
            "langsung teks pasal tertentu dari KUHP_Baru.txt?"
        )
    )

    need_tool: bool = Field(
        description=(
            "Apakah diperlukan sumber eksternal melalui salah "
            "satu tool yang tersedia?"
        )
    )

    selected_tool: Optional[
        Literal[
            "Wikipedia",
            "arXiv",
            "TavilySearch"
        ]
    ] = Field(
        default=None,
        description=(
            "Tool eksternal yang paling sesuai jika memang "
            "diperlukan. Null jika tidak diperlukan."
        )
    )

    reasoning: str = Field(
        description=(
            "Penjelasan singkat mengenai keputusan router."
        )
    )


# ================================
# 🧠 NODE: VALIDASI + ROUTING LLM
# ================================
@traceable
def validation_node(
    state: AgentState
) -> AgentState:

    original_question = state["question"]

    history = state.get(
        "conversation_history",
        []
    )

    # --------------------------------
    # RESOLUSI KONTEKS OLEH LLM
    # --------------------------------
    q = resolve_contextual_question(
        original_question,
        history
    )

    # --------------------------------
    # ROUTER SEPENUHNYA OLEH LLM
    # --------------------------------
    router = llm.with_structured_output(
        RouterDecision
    )

    history_text = format_conversation_history(
        history
    )

    prompt = f"""
Anda adalah reasoning router untuk sebuah asisten hukum
yang berfokus pada Kitab Undang-Undang Hukum Pidana (KUHP)
Baru Indonesia.

Tugas Anda adalah memahami MAKSUD pertanyaan pengguna,
bukan melakukan pencocokan keyword.

Jangan menggunakan aturan deterministik berbasis keyword.

Jangan menganggap sebuah pertanyaan berada di dalam atau
di luar cakupan hanya karena terdapat atau tidak terdapat
kata tertentu.

Gunakan konteks, semantik, maksud pengguna, dan hubungan
antarpertanyaan untuk mengambil keputusan.

========================
TUJUAN ROUTING
========================

Tentukan:

1. Apakah pertanyaan secara substantif berkaitan dengan
   KUHP Baru Indonesia.

2. Jika berkaitan, tentukan apakah terdapat pasal tertentu
   yang relevan dan perlu diambil dari KUHP_Baru.txt.

3. Tentukan apakah informasi dari sumber eksternal diperlukan.

4. Jika sumber eksternal diperlukan, pilih tool yang paling
   sesuai dari tool yang tersedia.

Tool yang tersedia:

- Wikipedia
- arXiv
- TavilySearch

Jangan memilih tool hanya karena tersedia.

Jika KUHP_Baru.txt sudah cukup untuk menjawab pertanyaan,
tidak perlu menggunakan tool eksternal.

Jika sumber eksternal benar-benar diperlukan, pilih tool
yang paling sesuai.

========================
PRINSIP UTAMA
========================

Keputusan harus berasal dari pemahaman LLM terhadap
pertanyaan.

Jangan menggunakan daftar istilah yang telah ditentukan
sebelumnya.

Jangan menganggap topik tertentu otomatis relevan atau
tidak relevan.

Pertanyaan yang tampaknya berhubungan secara tidak langsung
tetap harus dinilai berdasarkan maknanya.

Jika pertanyaan tidak berkaitan dengan KUHP Baru,
relevant harus false.

Jika tidak berkaitan, tidak perlu memilih pasal dan
tidak perlu memilih tool.

Jika berkaitan tetapi tidak menyebut nomor pasal secara
eksplisit, Anda tetap boleh menentukan article_number jika
dari konteks percakapan memang dapat diidentifikasi dengan
cukup jelas.

Jika tidak dapat diidentifikasi, gunakan null.

========================
RIWAYAT
========================

{history_text}

========================
PERTANYAAN
========================

{q}
"""

    try:

        decision = router.invoke(
            prompt
        )

    except Exception as e:

        return {
            **state,
            "question": q,
            "relevant": False,
            "answer": (
                "Saya tidak mengetahui jawaban tersebut."
            ),
            "selected_tools": [],
            "direct_article": False,
            "article_number": None,
            "article_text": None,
            "reasoning": (
                f"Router LLM gagal memproses pertanyaan: {e}"
            )
        }

    # --------------------------------
    # OUT OF SCOPE
    # --------------------------------
    if not decision.relevant:

        return {
            **state,
            "question": q,
            "relevant": False,
            "answer": (
                "Saya tidak mengetahui jawaban tersebut "
                "karena pertanyaan ini tidak dapat dipastikan "
                "berkaitan dengan KUHP Baru."
            ),
            "selected_tools": [],
            "direct_article": False,
            "article_number": None,
            "article_text": None,
            "reasoning": decision.reasoning
        }

    # --------------------------------
    # ARTICLE
    # --------------------------------
    article_number = decision.article_number

    article_text = None

    if (
        decision.direct_article
        and article_number is not None
    ):

        article_text = extract_article(
            article_number
        )

    # --------------------------------
    # TOOL
    # --------------------------------
    selected_tools = []

    if decision.need_tool:

        if decision.selected_tool in tools:

            selected_tools = [
                decision.selected_tool
            ]

    return {
        **state,

        "question": q,

        "relevant": True,

        "article_number": article_number,

        "article_text": article_text,

        "direct_article": (
            decision.direct_article
            and article_number is not None
        ),

        "selected_tools": selected_tools,

        "reasoning": decision.reasoning,

        "answer": None
    }


# ================================
# 🧠 NODE: TOOL SELECTION
# ================================
@traceable
def tool_selection_node(
    state: AgentState
) -> AgentState:

    # --------------------------------
    # PASAL LANGSUNG
    # --------------------------------
    if state.get("direct_article"):

        return {
            **state,
            "selected_tools": [],
            "reasoning": state.get(
                "reasoning",
                "LLM menentukan bahwa teks pasal "
                "diperlukan dari KUHP_Baru.txt."
            )
        }

    # --------------------------------
    # OUT OF SCOPE
    # --------------------------------
    if not state.get("relevant"):

        return {
            **state,
            "selected_tools": []
        }

    # --------------------------------
    # TOOL SUDAH DIPILIH OLEH LLM
    # --------------------------------
    return {
        **state,
        "selected_tools": state.get(
            "selected_tools",
            []
        )
    }


# ================================
# 🔍 NODE: RETRIEVAL
# ================================
@traceable
def multi_source_retrieve_node(
    state: AgentState
) -> AgentState:

    # --------------------------------
    # PASAL -> LANGSUNG DOKUMEN
    # --------------------------------
    if state.get("direct_article"):

        article_text = state.get(
            "article_text"
        )

        if article_text:

            return {
                **state,
                "docs": [
                    article_text
                ],
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
    if not state.get("relevant"):

        return {
            **state,
            "docs": [],
            "external_docs": []
        }

    # --------------------------------
    # PERTANYAAN UMUM
    # --------------------------------
    q = state["question"]

    selected = state.get(
        "selected_tools",
        []
    )

    # KUHP tetap menjadi sumber utama.
    internal_docs = documents

    external_docs = []

    # --------------------------------
    # EXTERNAL TOOL
    # --------------------------------
    for tool_name in selected:

        if tool_name not in tools:
            continue

        try:

            result = tools[
                tool_name
            ].run(q)

            if isinstance(
                result,
                list
            ):

                result_str = ""

                for i, item in enumerate(
                    result
                ):

                    if isinstance(
                        item,
                        dict
                    ):

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
                    result_str.strip()
                )

            else:

                external_docs.append(
                    str(result)
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
# 🧩 NODE: GENERATE FINAL ANSWER
# ================================
@traceable
def enhanced_generation_node(
    state: AgentState
) -> AgentState:

    # --------------------------------
    # OUT OF SCOPE
    # --------------------------------
    if not state.get("relevant"):

        return {
            **state,
            "answer": (
                "Saya tidak mengetahui jawaban tersebut."
            )
        }

    # --------------------------------
    # PASAL TIDAK DITEMUKAN
    # --------------------------------
    if (
        state.get("direct_article")
        and not state.get("article_text")
    ):

        article_number = state.get(
            "article_number"
        )

        return {
            **state,
            "answer": (
                f"Teks Pasal {article_number} "
                f"tidak ditemukan dalam "
                f"KUHP_Baru.txt."
            )
        }

    # --------------------------------
    # PASAL DITEMUKAN
    # --------------------------------
    if state.get("direct_article"):

        article_number = state.get(
            "article_number"
        )

        article_text = state.get(
            "article_text"
        )

        history = format_conversation_history(
            state.get(
                "conversation_history",
                []
            )
        )

        # ==================================
        # LLM MENENTUKAN JENIS JAWABAN
        # ==================================
        class ArticleResponse(BaseModel):

            response_type: Literal[
                "quote",
                "explanation"
            ] = Field(
                description=(
                    "Tentukan apakah pengguna meminta "
                    "teks/bunyi pasal atau meminta penjelasan "
                    "mengenai pasal."
                )
            )

            answer: str = Field(
                description=(
                    "Jawaban final berdasarkan teks pasal "
                    "yang diberikan."
                )
            )

        article_llm = llm.with_structured_output(
            ArticleResponse
        )

        prompt = f"""
Anda adalah asisten yang menjelaskan KUHP Baru Indonesia.

Gunakan hanya teks Pasal {article_number} yang diberikan
sebagai dasar hukum untuk menjawab.

Jangan mengarang.

Jangan menambahkan ketentuan yang tidak ada.

Jangan menggunakan pengetahuan hukum internal model untuk
mengisi informasi yang tidak terdapat dalam teks.

Gunakan kemampuan memahami bahasa untuk menentukan maksud
pertanyaan pengguna.

Jika pengguna meminta bunyi, isi, kutipan, atau teks pasal,
tampilkan isi pasal berdasarkan sumber.

Jika pengguna meminta penjelasan, jelaskan berdasarkan
teks pasal.

Jika informasi yang ditanyakan tidak terdapat dalam teks
pasal, nyatakan keterbatasan tersebut.

Jangan membuat isi hukum baru.

========================
RIWAYAT
========================

{history}

========================
TEKS PASAL
========================

{article_text}

========================
PERTANYAAN
========================

{state["question"]}
"""

        try:

            result = article_llm.invoke(
                prompt
            )

            # Jika LLM memilih quote,
            # tetap gunakan formatter lokal agar
            # teks sumber tidak berubah.
            if result.response_type == "quote":

                answer = format_article_answer(
                    article_number,
                    article_text
                )

            else:

                answer = result.answer.strip()

            return {
                **state,
                "answer": answer
            }

        except Exception:

            return {
                **state,
                "answer": (
                    format_article_answer(
                        article_number,
                        article_text
                    )
                )
            }

    # --------------------------------
    # PERTANYAAN UMUM
    # --------------------------------
    q = state["question"]

    history = format_conversation_history(
        state.get(
            "conversation_history",
            []
        )
    )

    context = "\n".join(
        state.get("docs", []) +
        state.get("external_docs", [])
    )

    prompt = f"""
Anda adalah asisten hukum yang berfokus pada
Kitab Undang-Undang Hukum Pidana (KUHP) Baru Indonesia.

Pertanyaan pengguna telah dinilai oleh router sebagai
pertanyaan yang berkaitan dengan KUHP Baru.

Jawab pertanyaan berdasarkan sumber yang diberikan.

PRINSIP:

- Prioritaskan KUHP_Baru.txt.
- Gunakan sumber eksternal hanya jika tersedia dan memang
  relevan terhadap pertanyaan.
- Jangan mengarang isi hukum.
- Jangan membuat nomor pasal.
- Jangan membuat bunyi pasal.
- Jangan membuat sanksi atau unsur pidana yang tidak
  terdapat dalam sumber.
- Jika informasi tidak ditemukan dalam sumber, nyatakan
  bahwa informasi tersebut tidak ditemukan.
- Jangan menyamarkan ketidakpastian sebagai fakta.
- Gunakan conversation history untuk memahami pertanyaan
  lanjutan.
- Jawaban harus menjawab maksud pengguna, bukan sekadar
  mengulang sumber.

========================
RIWAYAT PERCAKAPAN
========================

{history}

========================
PERTANYAAN
========================

{q}

========================
SUMBER
========================

{context}

========================
JAWABAN
========================

Berikan jawaban dalam bahasa Indonesia yang jelas,
natural, dan mudah dipahami.
"""

    res = llm.invoke(
        prompt
    )

    return {
        **state,
        "answer": res.content.strip()
    }


# ================================
# 🔧 WORKFLOW GRAPH
# ================================
workflow = StateGraph(
    AgentState
)


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


workflow.set_entry_point(
    "Validation"
)


# ================================
# 🔀 CONDITIONAL ROUTING
# ================================
workflow.add_conditional_edges(

    "Validation",

    lambda s: (

        "DirectAnswer"

        if s.get("direct_article")

        else (

            "OutOfScope"

            if not s.get("relevant")

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


# ================================
# 🚀 COMPILE
# ================================
runnable_graph = workflow.compile()
