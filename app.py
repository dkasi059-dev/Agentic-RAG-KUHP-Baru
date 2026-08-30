import os
import streamlit as st
from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.tools import Tool
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph, END
from langsmith import traceable
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

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
    model="thinkingmachines/inkling-small:free",
    temperature=0,
    openai_api_key=st.secrets["API_OR"],
    openai_api_base="https://openrouter.ai/api/v1"
)

# ================================
# 🧰 Tools
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
# 🧩 Agent State (ditambah retrieved_items)
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
    retrieved_items: Optional[Dict[str, Any]]  # menyimpan hasil retrieval dari tools

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

    Tugas:
    1. Tentukan apakah pertanyaan ini BERKAITAN dengan KUHP baru. Jika tidak, jawab: RELEVANT: no dan REASONING.
    2. Jika berkaitan, pilih tools yang paling sesuai dari:
       - Wikipedia: konsep hukum umum (Bahasa Indonesia)
       - arXiv: penelitian hukum akademik
       - TavilySearch: berita, informasi terkini, artikel internet, putusan pengadilan
       - Dokumen KUHP Baru: isi pasal-pasal (sudah tersedia secara internal)
    3. Sangat wajib sekali untuk memperhatikan riwayat percakapan sebelumnya baru menentukan apakah berkaitan dengan pertanyaan sebelumnya atau tidak?
    4. Jika diminta ayat maka jangan tafsirkan pasal. Misalnya ayat 1 maka lihat percakapan sebelumnya membicarakan pasal berapa? berarti ayat dalam pasal itulah yang dimaksud.
    Pertimbangkan konteks riwayat: jika sebelumnya Anda telah memberikan daftar hasil dari dokumen KUHP_Baru.txt maupun pencarian dari TavilySearch dan pertanyaan sekarang merujuk pada ayat, pasal, atau nomor urut tertentu (misal: pertama, kedua, kelima, atau angka 1,2,3), maka tidak perlu memilih TavilySearch lagi, cukup gunakan hasil retrieval yang sudah ada. Namun jika pertanyaannya tidak ada hubungannya dengan pertanyaan sebelumnya, gunakan TavilySearch.

    Format jawaban (jika berkaitan):
    RELEVANT: yes
    TOOLS: tool1,tool2
    REASONING: alasan
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
    retrieved_items = {}

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
                    retrieved_items[tool_name] = result  # simpan list asli
                else:
                    external_docs.append(str(result))
                    retrieved_items[tool_name] = str(result)
            except Exception as e:
                external_docs.append(f"{tool_name} gagal: {str(e)}")
                retrieved_items[tool_name] = f"Error: {str(e)}"

    return {
        **state,
        "docs": internal_docs,
        "external_docs": external_docs,
        "retrieved_items": retrieved_items
    }

# ================================
# 🧩 Node: Generate Final Answer
# ================================
@traceable
def enhanced_generation_node(state: AgentState) -> AgentState:
    q = state["question"]
    internal_context = "\n".join(state.get("docs", []))
    external_context = "\n".join(state.get("external_docs", []))
    retrieved = state.get("retrieved_items", {})

    # Format hasil retrieval dari TavilySearch (atau tool lain) dengan nomor urut
    # Kita ambil hasil dari semua tool yang mengembalikan list (misal TavilySearch)
    formatted_items = []
    for tool_name, items in retrieved.items():
        if isinstance(items, list):
            for idx, item in enumerate(items, start=1):
                if isinstance(item, dict):
                    # Asumsikan item memiliki 'title', 'content', 'link' dll.
                    title = item.get('title', 'No title')
                    content = item.get('content', '')
                    link = item.get('link', '')
                    formatted_items.append(f"{idx}. {title}\n   {content}\n   Link: {link}")
                else:
                    formatted_items.append(f"{idx}. {str(item)}")
        else:
            # jika hasil berupa string, kita masukkan sebagai satu item
            formatted_items.append(f"1. {str(items)}")

    if formatted_items:
        items_text = "Daftar hasil pencarian:\n" + "\n\n".join(formatted_items)
        external_context = items_text + "\n\n" + external_context

    history = state.get("history", [])
    history_text = ""
    for msg in history[-6:]:
        history_text += f"{msg['role']}: {msg['content']}\n"

    prompt = f"""
    Anda adalah asisten ahli Kitab Undang-Undang Hukum Pidana (KUHP) baru di Indonesia.
    Riwayat percakapan:
    {history_text}

    Pertanyaan: {q}

    Konteks yang tersedia:
    --- DOKUMEN KUHP (internal) ---
    {internal_context}

    --- HASIL PENCARIAN EKSTERNAL ---
    {external_context}

    Instruksi:
    - Gunakan sumber yang paling relevan untuk menjawab pertanyaan.
    - Jika pertanyaan merujuk pada nomor urut tertentu dari daftar hasil pencarian (misal: "pertama", "kedua", "kelima", "nomor 1", "item ke-3", dsb.), maka jawablah berdasarkan item yang sesuai dari daftar tersebut.
    - Jika pertanyaan menanyakan isi spesifik dari KUHP (misal pasal atau bab), gunakan dokumen internal.
    - Sertakan sumber informasi (misal: KUHP, Wikipedia, Tavily, arXiv) secara jelas.
    - Jika informasi tidak tersedia, sampaikan dengan jujur.
    - Jawab dengan bahasa Indonesia formal dan ringkas.
    - Jika diminta ayat maka jangan tafsirkan pasal. Misalnya ayat 1 maka lihat percakapan sebelumnya membicarakan pasal berapa? berarti ayat dalam pasal itulah yang dimaksud.
    """

    res = llm.invoke(prompt)
    return {**state, "answer": res.content.strip(), "answered": True}

# ================================
# 🔧 Workflow Graph (LangGraph)
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
