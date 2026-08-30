import streamlit as st
import datetime
import pytz
import app
import html

# ================================
# KONFIGURASI HALAMAN
# ================================
st.set_page_config(
    page_title="Chatbot Pintar KUHP Baru",
    page_icon="⚖️",
    layout="wide",
)

# ================================
# CSS
# ================================
st.markdown(
"""
<style>

/* =========================================================
   GLOBAL
========================================================= */

.stApp {
    background:
        radial-gradient(
            circle at 50% -15%,
            rgba(148, 163, 184, 0.16) 0%,
            rgba(148, 163, 184, 0) 38%
        ),
        linear-gradient(
            145deg,
            #0b1220 0%,
            #111827 48%,
            #1e293b 100%
        );

    color: #f8fafc !important;
    font-family: "Segoe UI", "Inter", Arial, sans-serif;
}


/* =========================================================
   MAIN CONTAINER
========================================================= */

.block-container {
    max-width: 1280px;
    padding-top: 1.6rem;
    padding-bottom: 5rem;
}


/* =========================================================
   LOGO
========================================================= */

.logo-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 4px;
    margin-bottom: 20px;
}

.logo-wrapper img {
    width: 270px;
    max-width: 65vw;

    border-radius: 24px;

    box-shadow:
        0 20px 45px rgba(0, 0, 0, 0.42),
        0 0 0 1px rgba(255, 255, 255, 0.08);

    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease;
}

.logo-wrapper img:hover {
    transform: scale(1.02);

    box-shadow:
        0 24px 55px rgba(0, 0, 0, 0.50),
        0 0 0 1px rgba(255, 255, 255, 0.14);
}


/* =========================================================
   HEADER
========================================================= */

.header-box {
    max-width: 1000px;
    margin: 0 auto 30px auto;

    padding: 8px 30px 24px 30px;

    text-align: center;

    border-bottom:
        1px solid rgba(148, 163, 184, 0.25);
}

.main-title {
    text-align: center;

    font-size: clamp(25px, 3vw, 38px);
    line-height: 1.25;

    font-weight: 750;

    color: #f8fafc !important;

    margin: 0 auto 12px auto;

    letter-spacing: -0.5px;

    text-shadow:
        0 3px 14px rgba(0, 0, 0, 0.38);
}

p.subtitle {
    text-align: center;

    font-size: 15.5px;
    line-height: 1.8;

    color: #cbd5e1 !important;

    margin: 0 auto;

    max-width: 820px;
}

p.subtitle b {
    color: #d6a58d !important;
}


/* =========================================================
   CHAT AREA
========================================================= */

.chat-container {
    background:
        linear-gradient(
            145deg,
            rgba(255, 255, 255, 0.075),
            rgba(255, 255, 255, 0.025)
        );

    border:
        1px solid rgba(255, 255, 255, 0.09);

    border-radius: 24px;

    padding: 26px;

    min-height: 100px;

    max-height: 70vh;

    overflow-y: auto;

    box-shadow:
        0 20px 50px rgba(0, 0, 0, 0.28),
        inset 0 1px 0 rgba(255, 255, 255, 0.05);

    backdrop-filter: blur(12px);
}


/* =========================================================
   USER CHAT BUBBLE
========================================================= */

.chat-bubble-user {
    background:
        linear-gradient(
            135deg,
            #e2e8f0 0%,
            #cbd5e1 100%
        );

    color: #172033;

    padding: 15px 19px;

    border-radius:
        19px
        19px
        6px
        19px;

    margin:
        4px
        0
        18px
        auto;

    max-width: 78%;

    line-height: 1.7;

    border:
        1px solid rgba(255, 255, 255, 0.55);

    box-shadow:
        0 7px 20px rgba(0, 0, 0, 0.20);
}

.chat-bubble-user .chat-label {
    color: #334155;
    font-size: 13px;
    font-weight: 750;
    letter-spacing: 0.2px;
}

.chat-bubble-user .chat-text {
    margin-top: 5px;
}


/* =========================================================
   ASSISTANT CHAT BUBBLE
========================================================= */

.chat-bubble-assistant {
    background:
        linear-gradient(
            145deg,
            #ffffff 0%,
            #f8fafc 100%
        );

    color: #1e293b;

    padding: 16px 20px;

    border-radius:
        19px
        19px
        19px
        6px;

    margin:
        4px
        auto
        18px
        0;

    max-width: 84%;

    line-height: 1.75;

    border-left:
        4px solid #7f1d1d;

    box-shadow:
        0 8px 22px rgba(0, 0, 0, 0.20);
}

.chat-bubble-assistant .chat-label {
    color: #7f1d1d;
    font-size: 13px;
    font-weight: 750;
    letter-spacing: 0.2px;
}

.chat-bubble-assistant .chat-text {
    margin-top: 5px;
}


/* =========================================================
   ANALYSIS BOX
========================================================= */

.reasoning-box {
    margin-top: 14px;

    padding: 12px 15px;

    background: #f1f5f9;

    border-left:
        3px solid #64748b;

    border-radius: 10px;

    color: #475569;

    font-size: 13.5px;

    line-height: 1.65;
}

.reasoning-title {
    font-weight: 750;
    color: #334155;
}


/* =========================================================
   SIDEBAR
========================================================= */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            165deg,
            #f8fafc 0%,
            #e2e8f0 100%
        );

    color: #1e293b;

    border-right:
        1px solid rgba(15, 23, 42, 0.10);

    box-shadow:
        8px 0 28px rgba(0, 0, 0, 0.14);
}

[data-testid="stSidebar"] * {
    color: #1e293b;
}


/* =========================================================
   SIDEBAR HEADER
========================================================= */

.sidebar-header {
    text-align: center;

    font-weight: 800;

    font-size: 15px;

    letter-spacing: 0.8px;

    margin:
        26px
        0
        16px
        0;

    color: #172033;

    padding-bottom: 12px;

    border-bottom:
        1px solid rgba(71, 85, 105, 0.22);
}


/* =========================================================
   SIDEBAR BUTTON
========================================================= */

[data-testid="stSidebar"] button {

    background:
        #ffffff !important;

    color:
        #7f1d1d !important;

    font-weight:
        700 !important;

    border-radius:
        12px !important;

    border:
        1px solid rgba(127, 29, 29, 0.28) !important;

    box-shadow:
        0 4px 12px rgba(15, 23, 42, 0.08);

    transition:
        all 0.22s ease !important;
}

[data-testid="stSidebar"] button:hover {

    background:
        #7f1d1d !important;

    color:
        #ffffff !important;

    border:
        1px solid #7f1d1d !important;

    transform:
        translateY(-1px);

    box-shadow:
        0 7px 18px rgba(127, 29, 29, 0.22);
}


/* =========================================================
   SIDEBAR INFO
========================================================= */

[data-testid="stSidebar"] [data-testid="stAlert"] {

    background:
        rgba(255, 255, 255, 0.72);

    border:
        1px solid rgba(71, 85, 105, 0.16);

    border-radius:
        13px;

    color:
        #475569;
}


/* =========================================================
   CHAT INPUT
========================================================= */

[data-testid="stChatInput"] {
    border-radius: 17px !important;
}

[data-testid="stChatInput"] > div {
    background: #f8fafc !important;

    border:
        1px solid rgba(148, 163, 184, 0.35) !important;

    border-radius: 17px !important;

    box-shadow:
        0 10px 28px rgba(0, 0, 0, 0.16) !important;
}

[data-testid="stChatInput"] textarea {
    font-size: 15px !important;
    color: #1e293b !important;
}


/* =========================================================
   ALERT / SPINNER
========================================================= */

[data-testid="stAlert"] {
    border-radius: 12px;
}


/* =========================================================
   SCROLLBAR
========================================================= */

::-webkit-scrollbar {
    width: 7px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.04);
}

::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.40);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(148, 163, 184, 0.60);
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .logo-wrapper img {
        width: 210px;
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
""",
unsafe_allow_html=True
)


# ================================
# SESSION STATE
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
# SIDEBAR
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
        """
<div class="sidebar-header">
RIWAYAT PERTANYAAN ANDA
</div>
""",
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
# LOGO
# ================================
try:

    st.markdown(
        '<div class="logo-wrapper">',
        unsafe_allow_html=True
    )

    st.image(
        "logo.png",
        width=270
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

except Exception:
    pass


# ================================
# HEADER
# ================================
st.markdown(
"""
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
""",
unsafe_allow_html=True
)


# ================================
# AREA CHAT
# ================================
chat_box = st.container()

with chat_box:

    st.markdown(
        '<div class="chat-container">',
        unsafe_allow_html=True
    )


    for msg in st.session_state.messages:

        role = msg["role"]
        text = msg["text"]
        time = msg["time"]


        # =====================================================
        # USER MESSAGE
        # =====================================================

        if role == "user":

            safe_text = html.escape(
                str(text)
            ).replace(
                "\n",
                "<br>"
            )

            st.markdown(
f"""
<div class="chat-bubble-user">
    <div class="chat-label">
        Anda &nbsp;•&nbsp; {html.escape(str(time))}
    </div>

    <div class="chat-text">
        {safe_text}
    </div>
</div>
""",
                unsafe_allow_html=True
            )


        # =====================================================
        # ASSISTANT MESSAGE
        # =====================================================

        else:

            # Pisahkan reasoning dari jawaban jika ada.
            marker = "<br><br>🧠 <b>Analisis:</b>"

            if marker in str(text):

                answer_part, reasoning_part = str(text).split(
                    marker,
                    1
                )

                safe_answer = html.escape(
                    answer_part
                ).replace(
                    "\n",
                    "<br>"
                )

                safe_reasoning = html.escape(
                    reasoning_part
                ).replace(
                    "\n",
                    "<br>"
                )

                assistant_html = f"""
<div class="chat-bubble-assistant">

    <div class="chat-label">
        ⚖️ Jawaban Chatbot Suhardi
        &nbsp;•&nbsp;
        {html.escape(str(time))}
    </div>

    <div class="chat-text">
        {safe_answer}
    </div>

    <div class="reasoning-box">
        <span class="reasoning-title">
            🧠 Analisis
        </span>
        <br>
        {safe_reasoning}
    </div>

</div>
"""

            else:

                safe_answer = html.escape(
                    str(text)
                ).replace(
                    "\n",
                    "<br>"
                )

                assistant_html = f"""
<div class="chat-bubble-assistant">

    <div class="chat-label">
        ⚖️ Jawaban Chatbot Suhardi
        &nbsp;•&nbsp;
        {html.escape(str(time))}
    </div>

    <div class="chat-text">
        {safe_answer}
    </div>

</div>
"""


            st.markdown(
                assistant_html,
                unsafe_allow_html=True
            )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ================================
# INPUT CHAT
# ================================
if st.session_state.viewing_history_index is None:

    prompt = st.chat_input(
        "💬 Tuliskan pertanyaan Anda seputar KUHP Baru..."
    )


    if prompt:

        tz = pytz.timezone(
            "Asia/Jakarta"
        )

        current_time = datetime.datetime.now(
            tz
        ).strftime("%H:%M:%S")


        # --------------------------------
        # Simpan pertanyaan user
        # --------------------------------

        st.session_state.messages.append({
            "role": "user",
            "text": prompt,
            "time": current_time
        })


        st.session_state.pending_prompt = prompt

        st.rerun()


    # ================================
    # PROSES PERTANYAAN
    # ================================
    if st.session_state.pending_prompt:

        with st.spinner(
            "🔍 Sedang menganalisis dengan Agentic RAG..."
        ):

            try:

                # --------------------------------
                # Ambil seluruh riwayat
                # kecuali pertanyaan terakhir
                # --------------------------------

                conversation_history = (
                    st.session_state.messages[:-1].copy()
                )


                # --------------------------------
                # Ubah text -> content
                # --------------------------------

                history_for_agent = [
                    {
                        "role": msg["role"],
                        "content": msg["text"]
                    }
                    for msg in conversation_history
                ]


                # --------------------------------
                # State untuk Agent
                # --------------------------------

                state = {
                    "question":
                        st.session_state.pending_prompt,

                    "history":
                        history_for_agent
                }


                # --------------------------------
                # Jalankan Agentic RAG
                # --------------------------------

                result = app.runnable_graph.invoke(
                    state
                )


                # --------------------------------
                # Ambil jawaban
                # --------------------------------

                answer = result.get(
                    "answer",
                    "Tidak ada jawaban ditemukan."
                )


                reasoning = result.get(
                    "reasoning",
                    ""
                )


                # --------------------------------
                # Bentuk response
                # --------------------------------

                if reasoning:

                    response_text = (
                        f"{answer}"
                        f"<br><br>"
                        f"🧠 <b>Analisis:</b>"
                        f"{reasoning}"
                    )

                else:

                    response_text = answer


            except Exception as e:

                response_text = (
                    f"⚠️ Terjadi kesalahan: "
                    f"{str(e)}"
                )


        # ================================
        # SIMPAN JAWABAN
        # ================================

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
