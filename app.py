import os
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
os.environ["TAVILY_API_KEY"] = "TAVILY_API_KEY"
os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["LANGCHAIN_PROJECT"]

# ================================
# 🔮 Setup Google Gemini (via OpenRouter)
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
wikipedia_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="id"))
arxiv_tool = ArxivQueryRun(api_wrapper=ArxivAPIWrapper())
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
# 📚 Load Dokumen KUHP Baru
# ================================
with open("KUHP_Baru.txt", "r", encoding="utf-8") as f:
    documents = [f.read()]

# ================================
# 🧩 Define Agent State (ditambah history)
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
    history: Optional[List[dict]]

# ================================
# 🧠 Node: Tool Selection + Relevansi
# ================================
@traceable
def tool_selection_node(state: AgentState) -> AgentState:
    q = state["question"]
    history = state.get("history", [])
    history_text = ""
    for msg in history[-6:]:
        history_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
    Anda adalah asisten ahli Kitab Undang-Undang Hukum Pidana (KUHP) baru di Indonesia.
    Riwayat percakapan:
    {history_text}

    Pertanyaan terbaru: {q}

    Tugas Anda:
    1. Tentukan apakah pertanyaan ini BERKAITAN dengan Kitab Undang-Undang Hukum Pidana (KUHP) baru atau tidak.
       Jika tidak, jawab: RELEVANT: no dan berikan REASONING.
    2. Jika berkaitan, pilih tools yang paling sesuai dari daftar berikut:
       - Wikipedia (konsep hukum umum, Bahasa Indonesia) – untuk penjelasan konsep dasar.
       - arXiv (penelitian hukum akademik) – untuk teori/penelitian ilmiah.
       - TavilySearch (berita dan hukum terbaru di Indonesia) – WAJIB digunakan jika pertanyaan meminta informasi terkini, artikel dari internet, berita, putusan pengadilan, atau hal-hal yang memerlukan pencarian web.
       - Dokumen KUHP Baru (isi pasal-pasal, tersedia secara internal) – untuk isi spesifik pasal.

    **Penting**: Jika pertanyaan meminta "judul artikel", "berita", "informasi terbaru", atau "cari di internet", maka TavilySearch HARUS dipilih.

    Format jawaban (hanya jika berkaitan):
    RELEVANT: yes
    TOOLS: tool1,tool2 (pisahkan dengan koma)
    REASONING: alasan pemilihan tools

    Jawaban akhir hanya akan dihasilkan jika RELEVANT: yes.
    """

    result = llm.invoke(prompt)
    lines = result.content.strip().split("\n")
    relevant = False
    tools_selected = []
    reasoning = ""

    for line in lines:
        if line.startswith("RELEVANT:"):
            val = line.replace("RELEVANT:", "").strip().lower()
            relevant = val == "yes"
        elif line.startswith("TOOLS:"):
            tools_selected = [t.strip() for t in line.replace("TOOLS:", "").split(",") if t.strip()]
        elif line.startswith("REASONING:"):
            reasoning = line.replace("REASONING:", "").strip()

    if not relevant:
        return {
            **state,
            "answer": "saya tidak bisa menjawab pertanyaan Anda karena tidak berkaitan dengan Kitab Undang-Undang Hukum Pidana (KUHP) baru",
            "answered": True,
            "relevant": False,
            "selected_tools": [],
            "reasoning": reasoning
        }

    # Pastikan TavilySearch dipilih jika pertanyaan mengandung kata "artikel", "internet", "berita", "terbaru"
    # Jika tidak, kita bisa menambahkan secara paksa, tapi lebih baik biarkan LLM memutuskan.
    # Namun untuk memastikan, kita bisa periksa kata kunci.
    # Saya tidak menambahkan logika paksa agar tetap fleksibel.

    return {
        **state,
        "relevant": True,
        "answered": False,
        "selected_tools": tools_selected,
        "reasoning": reasoning
    }

# ================================
# 🔍 Node: Multi Source Retrieval
# ================================
@traceable
def multi_source_retrieve_node(state: AgentState) -> AgentState:
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
                            result_str += f"Result {i+1}: {item.get('title', 'No title')} - {item.get('content', 'No content')}\n"
                        else:
                            result_str += f"Result {i+1}: {str(item)}\n"
                    external_docs.append(result_str.strip())
                else:
                    external_docs.append(str(result))
            except Exception as e:
                external_docs.append(f"{tool_name} gagal: {str(e)}")

    return {**state, "docs": internal_docs, "external_docs": external_docs}

# ================================
# 🧩 Node: Generate Final Answer
# ================================
@traceable
def enhanced_generation_node(state: AgentState) -> AgentState:
    q = state["question"]
    context = "\n".join(state.get("docs", []) + state.get("external_docs", []))
    history = state.get("history", [])
    history_text = ""
    for msg in history[-6:]:
        history_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
    Anda adalah asisten ahli Kitab Undang-Undang Hukum Pidana (KUHP) baru di Indonesia.
    Riwayat percakapan:
    {history_text}

    Pertanyaan: {q}

    Gunakan konteks berikut (utamakan dokumen KUHP Baru, tetapi jika ada hasil pencarian dari TavilySearch, Wikipedia, atau arXiv, gunakan juga) untuk menjawab secara komprehensif dan akurat.
    Konteks:
    {context}

    Jawablah dengan bahasa Indonesia formal, sertakan sumber informasi (misal: KUHP, Wikipedia, Tavily, arXiv) jika relevan.
    Jika jawaban tidak ditemukan dalam konteks, sampaikan bahwa informasi tidak tersedia.
    Jika hasil pencarian dari TavilySearch berisi judul-judul artikel, sebutkan judul-judul tersebut dengan jelas.
    """

    res = llm.invoke(prompt)
    return {**state, "answer": res.content.strip(), "answered": True}

# ================================
# 🔧 Workflow Graph (LangGraph) - Tanpa loop & evaluasi berlebih
# ================================
workflow = StateGraph(AgentState)
workflow.add_node("ToolSelection", tool_selection_node)
workflow.add_node("Retrieve", multi_source_retrieve_node)
workflow.add_node("Generate", enhanced_generation_node)

workflow.set_entry_point("ToolSelection")
workflow.add_conditional_edges(
    "ToolSelection",
    lambda state: "END" if state.get("answered") else "Retrieve",
    {
        "Retrieve": "Retrieve",
        "END": END
    }
)
workflow.add_edge("Retrieve", "Generate")
workflow.add_edge("Generate", END)

runnable_graph = workflow.compile()
