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

/* ================================
   GLOBAL
================================ */
.stApp {
    background:
        radial-gradient(
            circle at 50% -10%,
            rgba(39, 174, 96, 0.18) 0%,
            rgba(11, 61, 46, 0) 38%
        ),
        linear-gradient(
            145deg,
            #061a14 0%,
            #0b3d2e 48%,
            #115c42 100%
        );

    color: #f8f9fa !important;
    font-family: "Segoe UI", sans-serif;
}

/* Sedikit memperlebar area utama */
.block-container {
    max-width: 1200px;
    padding-top: 1.8rem;
    padding-bottom: 5rem;
}


/* ================================
   LOGO
================================ */
.logo-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 4px;
    margin-bottom: 18px;
}

.logo-wrapper img {
    width: 190px;
    max-width: 45vw;

    border-radius: 24px;

    filter:
        drop-shadow(0 10px 22px rgba(0, 0, 0, 0.40))
        drop-shadow(0 0 15px rgba(212, 175, 55, 0.12));

    transition:
        transform 0.3s ease,
        filter 0.3s ease;
}

.logo-wrapper img:hover {
    transform: scale(1.025);

    filter:
        drop-shadow(0 12px 26px rgba(0, 0, 0, 0.48))
        drop-shadow(0 0 20px rgba(212, 175, 55, 0.20));
}


/* ================================
   HEADER
================================ */
.header-box {
    max-width: 920px;
    margin: 0 auto 26px auto;

    padding:
        5px
        30px
        22px
        30px;

    text-align: center;

    border-bottom:
        1px solid rgba(212, 175, 55, 0.28);
}

.main-title {
    text-align: center;

    font-size: clamp(25px, 3vw, 36px);
    line-height: 1.25;

    font-weight: 750;

    color: #f4e4a6 !important;

    margin:
        0
        auto
        10px
        auto;

    letter-spacing: -0.4px;

    text-shadow:
        0 2px 10px rgba(0, 0, 0, 0.35);
}

p.subtitle {
    text-align: center;

    font-size: 15.5px;
    line-height: 1.75;

    color: #e8f5ee !important;

    margin:
        0
        auto;

    max-width: 780px;
}

p.subtitle b {
    color: #f4d875;
}


/* ================================
   CHAT AREA
================================ */
.chat-container {
    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.085),
            rgba(255, 255, 255, 0.035)
        );

    border:
        1px solid rgba(255, 255, 255, 0.10);

    border-radius: 22px;

    padding: 24px;

    max-height: 70vh;

    overflow-y: auto;

    box-shadow:
        0 18px 45px rgba(0, 0, 0, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.06);

    backdrop-filter: blur(8px);
}


/* ================================
   USER CHAT BUBBLE
================================ */
.chat-bubble-user {
    background:
        linear-gradient(
            135deg,
            #dff5e8 0%,
            #c9ead7 100%
        );

    color: #103c2d;

    padding: 14px 18px;

    border-radius:
        18px
        18px
        5px
        18px;

    margin:
        4px
        0
        16px
        auto;

    max-width: 78%;

    line-height: 1.65;

    border:
        1px solid rgba(255, 255, 255, 0.65);

    box-shadow:
        0 5px 16px rgba(0, 0, 0, 0.20);
}

.chat-bubble-user b {
    color: #08633e;
}


/* ================================
   ASSISTANT CHAT BUBBLE
================================ */
.chat-bubble-assistant {
    background:
        linear-gradient(
            145deg,
            #ffffff 0%,
            #f4f8f5 100%
        );

    color: #173c30;

    padding: 15px 19px;

    border-radius:
        18px
        18px
        18px
        5px;

    margin:
        4px
        auto
        16px
        0;

    max-width: 82%;

    line-height: 1.7;

    border-left:
        4px solid #d4af37;

    box-shadow:
        0 5px 16px rgba(0, 0, 0, 0.20);
}

.chat-bubble-assistant b {
    color: #8b6b12;
}


/* ================================
   SIDEBAR
================================ */
[data-testid="stSidebar"] {

    background:
        linear-gradient(
            165deg,
            #fff9cf 0%,
            #f7df72 55%,
            #e7bd36 100%
        );

    color: #183c30;

    border-right:
        1px solid rgba(0, 0, 0, 0.08);

    box-shadow:
        8px 0 28px rgba(0, 0, 0, 0.13);
}

[data-testid="stSidebar"] * {
    color: #183c30;
}

.sidebar-header {
    text-align: center;

    font-weight: 800;

    font-size: 16px;

    letter-spacing: 0.7px;

    margin:
        24px
        0
        14px
        0;

    color: #143c2c;

    padding-bottom: 10px;

    border-bottom:
        1px solid rgba(20, 60, 44, 0.20);
}


/* ================================
   SIDEBAR BUTTON
================================ */
[data-testid="stSidebar"] button {

    background:
        rgba(255, 255, 255, 0.83) !important;

    color:
        #7b151d !important;

    font-weight:
        700 !important;

    border-radius:
        11px !important;

    border:
        1px solid rgba(123, 21, 29, 0.45) !important;

    box-shadow:
        0 3px 10px rgba(0, 0, 0, 0.09);

    transition:
        all 0.22s ease !important;
}

[data-testid="stSidebar"] button:hover {

    background:
        #9f1d27 !important;

    color:
        #ffffff !important;

    border:
        1px solid #9f1d27 !important;

    transform:
        translateY(-1px);

    box-shadow:
        0 6px 16px rgba(104, 15, 22, 0.22);
}


/* ================================
   CHAT INPUT
================================ */
[data-testid="stChatInput"] {
    border-radius: 16px !important;
}

[data-testid="stChatInput"] textarea {
    font-size: 15px !important;
}


/* ================================
   STREAMLIT INFO / SPINNER
================================ */
[data-testid="stAlert"] {
    border-radius: 12px;
}


/* ================================
   RESPONSIVE
================================ */
@media (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .logo-wrapper img {
        width: 150px;
    }

    .header-box {
        padding-left: 8px;
        padding-right: 8px;
    }

    .main-title {
        font-size: 25px;
    }

    p.subtitle {
        font-size: 14px;
    }

    .chat-container {
        padding: 14px;
    }

    .chat-bubble-user,
    .chat-bubble-assistant {
        max-width: 94%;
    }
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
        "<div class='sidebar-header'>RIWAYAT PERTANYAAN ANDA</div>",
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
# 🌿 LOGO
# ================================
try:

    col_logo_left, col_logo, col_logo_right = st.columns(
        [4, 2, 4]
    )

    with col_logo:
        st.image(
            "logo.png",
            use_container_width=True
        )

except Exception:
    pass


# ================================
# 🌿 HEADER
# ================================
st.markdown("""
<div class="header-box">

    <div class="main-title">
        ⚖️ Chatbot Kitab Undang-Undang Hukum Pidana (KUHP) Baru
    </div>

    <p class="subtitle">
        Agentic RAG with LangChain
        <br>
        Tanyakan apa pun seputar
        <b>UU No. 1 Tahun 2023 tentang KUHP</b>.
        <br>
        Chatbot ini dibuat oleh
        <b>SUHARDI</b>.
    </p>

</div>
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
                    <b>Anda ({time})</b>
                    <br>
                    {text}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class='chat-bubble-assistant'>
                    <b>Jawaban Chatbot Suhardi ({time})</b>
                    <br>
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
    if st.session_state.pending_prompt:

        with st.spinner(
            "🔍 Sedang menganalisis dengan Agentic RAG..."
        ):

            try:

                # Ambil seluruh riwayat kecuali pertanyaan terakhir
                conversation_history = (
                    st.session_state.messages[:-1].copy()
                )

                # Ubah format:
                # 'text' menjadi 'content'
                # agar sesuai dengan agent
                history_for_agent = [
                    {
                        "role": msg["role"],
                        "content": msg["text"]
                    }
                    for msg in conversation_history
                ]

                state = {
                    "question":
                        st.session_state.pending_prompt,

                    "history":
                        history_for_agent
                }

                result = app.runnable_graph.invoke(
                    state
                )

                answer = result.get(
                    "answer",
                    "Tidak ada jawaban ditemukan."
                )

                reasoning = result.get(
                    "reasoning",
                    ""
                )

                if reasoning:

                    response_text = (
                        f"{answer}"
                        f"<br><br>"
                        f"🧠 <b>Analisis:</b> "
                        f"{reasoning}"
                    )

                else:

                    response_text = answer

            except Exception as e:

                response_text = (
                    f"⚠️ Terjadi kesalahan: "
                    f"{str(e)}"
                )

        tz = pytz.timezone(
            "Asia/Jakarta"
        )

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
