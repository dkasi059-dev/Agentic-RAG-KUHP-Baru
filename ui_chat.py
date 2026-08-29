import streamlit as st
import datetime
import pytz
import app

# ================================
# 🌿 KONFIGURASI HALAMAN
# ================================
st.set_page_config(
    page_title="Chatbot Pintar KUHP Baru",
    page_icon="⚖️",
    layout="wide",
)

# ================================
# 🌿 CSS
# ================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0b3d2e 0%, #198754 100%);
    color: #f8f9fa !important;
    font-family: "Segoe UI", sans-serif;
}
h2 {
    text-align: center;
    font-weight: 700;
    color: #d1f7c4 !important;
    margin-bottom: 5px;
}
p.subtitle {
    text-align: center;
    font-size: 15px;
    color: #e8ffe0;
    margin-bottom: 25px;
}
.chat-container {
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 20px;
    max-height: 70vh;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.chat-bubble-user {
    background: #d1e7dd;
    color: #0f5132;
    padding: 12px 18px;
    border-radius: 18px 18px 4px 18px;
    margin-bottom: 12px;
    max-width: 80%;
    margin-left: auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
.chat-bubble-assistant {
    background: #f8f9fa;
    color: #0f5132;
    padding: 12px 18px;
    border-radius: 18px 18px 18px 4px;
    margin-bottom: 12px;
    max-width: 80%;
    margin-right: auto;
    box-shadow: 0 2px 8px rgba(0,0,0,0.25);
}
[data-testid="stSidebar"] {
    background: linear-gradient(135deg, #fff176 0%, #fbc02d 100%);
    color: #1b4332;
}
.sidebar-header {
    text-align: center;
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 15px;
}
[data-testid="stSidebar"] button {
    background-color: #ffffff !important;
    color: #c1121f !important;
    font-weight: bold !important;
    border-radius: 10px !important;
    border: 2px solid #c1121f !important;
    transition: all 0.3s ease !important;
}
[data-testid="stSidebar"] button:hover {
    background-color: #c1121f !important;
    color: #ffffff !important;
    border: 2px solid #c1121f !important;
}
</style>
""", unsafe_allow_html=True)

# ================================
# 🌿 SESSION STATE
# ================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "viewing_history_index" not in st.session_state:
    st.session_state.viewing_history_index = None

# ================================
# 🌿 SIDEBAR
# ================================
with st.sidebar:

    if st.button(
        "MULAI CHAT BARU",
        use_container_width=True
    ):
        if (
            st.session_state.messages
            and st.session_state.viewing_history_index is None
        ):
            st.session_state.chat_history.append(
                st.session_state.messages.copy()
            )

        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.session_state.viewing_history_index = None

        st.rerun()

    st.markdown(
        "<div class='sidebar-header'>RIWAYAT PERTANYAAN ANDA:</div>",
        unsafe_allow_html=True
    )

    if st.session_state.chat_history:

        for i, chat in enumerate(
            reversed(st.session_state.chat_history),
            1
        ):

            first_msg = next(
                (
                    m["text"]
                    for m in chat
                    if m["role"] == "user"
                ),
                "(tanpa isi)"
            )

            short_preview = (
                first_msg[:60] + "..."
                if len(first_msg) > 60
                else first_msg
            )

            if st.button(
                short_preview,
                use_container_width=True,
                key=f"hist_{i}"
            ):
                st.session_state.messages = chat.copy()

                st.session_state.viewing_history_index = (
                    len(st.session_state.chat_history) - i
                )

                st.session_state.pending_prompt = None

                st.rerun()

    else:
        st.info(
            'Belum ada riwayat pertanyaan tersimpan. '
            'Riwayat akan tersimpan setelah Anda menekan '
            '"MULAI CHAT BARU".'
        )

# ================================
# 🌿 HEADER
# ================================
st.markdown("""
<h2>⚖️ Chatbot Kitab Undang-Undang Hukum Pidana (KUHP) Baru</h2>
<p class='subtitle'>
Agentic RAG with LangChain<br>
Tanyakan apa pun seputar <b>UU No. 1 Tahun 2023 tentang KUHP</b>.
<br>
Chatbot ini dibuat oleh <b>SUHARDI</b>.
</p>
""", unsafe_allow_html=True)

# ================================
# 💬 AREA CHAT
# ================================
chat_box = st.container()

with chat_box:

    st.markdown(
        "<div class='chat-container'>",
        unsafe_allow_html=True
    )

    for msg in st.session_state.messages:

        role = msg["role"]
        text = msg["text"]
        time = msg["time"]

        if role == "user":

            st.markdown(
                f"""
                <div class='chat-bubble-user'>
                <b>Anda ({time})</b><br>
                {text}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class='chat-bubble-assistant'>
                <b>Jawaban Chatbot Suhardi ({time})</b><br>
                {text}
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

# ================================
# 💬 INPUT CHAT
# ================================
if st.session_state.viewing_history_index is None:

    prompt = st.chat_input(
        "💬 Tuliskan pertanyaan Anda seputar KUHP Baru..."
    )

    if prompt:

        tz = pytz.timezone("Asia/Jakarta")

        current_time = datetime.datetime.now(
            tz
        ).strftime("%H:%M:%S")

        # Simpan pertanyaan user.
        st.session_state.messages.append({
            "role": "user",
            "text": prompt,
            "time": current_time
        })

        st.session_state.pending_prompt = prompt

        st.rerun()

    # ================================
    # 🧠 PROSES PERTANYAAN
    # ================================
# Di bagian proses pertanyaan
    if st.session_state.pending_prompt:
        with st.spinner("🔍 Sedang menganalisis dengan Agentic RAG..."):
            try:
                # Ambil seluruh riwayat kecuali pertanyaan terakhir
                conversation_history = st.session_state.messages[:-1].copy()
                # Ubah format: ubah 'text' menjadi 'content' agar sesuai dengan agent
                history_for_agent = [
                    {"role": msg["role"], "content": msg["text"]}
                    for msg in conversation_history
                ]
    
                state = {
                    "question": st.session_state.pending_prompt,
                    "history": history_for_agent   # <- gunakan field 'history'
                }
    
                result = app.runnable_graph.invoke(state)
                answer = result.get("answer", "Tidak ada jawaban ditemukan.")
                reasoning = result.get("reasoning", "")
                if reasoning:
                    response_text = f"{answer}<br><br>🧠 <b>Analisis:</b> {reasoning}"
                else:
                    response_text = answer
            except Exception as e:
                response_text = f"⚠️ Terjadi kesalahan: {str(e)}"

        tz = pytz.timezone("Asia/Jakarta")

        current_time = datetime.datetime.now(
            tz
        ).strftime("%H:%M:%S")

        st.session_state.messages.append({
            "role": "assistant",
            "text": response_text,
            "time": current_time
        })

        st.session_state.pending_prompt = None

        st.rerun()

else:

    st.info(
        "🔒 Anda sedang melihat riwayat chat lama. "
        "Klik 'MULAI CHAT BARU' untuk memulai percakapan baru."
    )
