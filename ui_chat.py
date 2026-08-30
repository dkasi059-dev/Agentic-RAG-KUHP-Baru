import streamlit as st
import datetime
import pytz
import app
import textwrap
import html


# ============================================================
# KONFIGURASI HALAMAN
# ============================================================

st.set_page_config(
    page_title="Chatbot Pintar KUHP Baru",
    page_icon="⚖️",
    layout="wide",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    textwrap.dedent(
        """
        <style>

        /* ====================================================
           PALET WARNA
           Navy      : #172033
           Navy Deep : #0D1424
           Ivory     : #F7F4EC
           Champagne : #C8A96B
           Slate     : #596579
           White     : #FFFFFF
        ==================================================== */


        /* ====================================================
           GLOBAL
        ==================================================== */

        .stApp {

            background:
                radial-gradient(
                    circle at 50% -15%,
                    rgba(200, 169, 107, 0.13) 0%,
                    rgba(200, 169, 107, 0.00) 34%
                ),
                linear-gradient(
                    145deg,
                    #0d1424 0%,
                    #172033 48%,
                    #202c42 100%
                );

            color: #f7f4ec !important;

            font-family:
                "Segoe UI",
                "Inter",
                Arial,
                sans-serif;
        }


        /* ====================================================
           HILANGKAN BEBERAPA ELEMEN DEFAULT STREAMLIT
        ==================================================== */

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            background: transparent !important;
        }


        /* ====================================================
           MAIN CONTAINER
        ==================================================== */

        .block-container {

            max-width: 1220px;

            padding-top: 1.5rem;
            padding-bottom: 5rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }


        /* ====================================================
           LOGO
        ==================================================== */

        .logo-wrapper {

            display: flex;

            justify-content: center;
            align-items: center;

            margin-top: 0;
            margin-bottom: 24px;
        }


        .logo-wrapper img {

            width: 250px !important;

            max-width: 65vw;

            height: auto;

            border-radius: 26px;

            filter:
                drop-shadow(
                    0 18px 35px
                    rgba(0, 0, 0, 0.42)
                )
                drop-shadow(
                    0 0 20px
                    rgba(200, 169, 107, 0.15)
                );

            transition:
                transform 0.3s ease,
                filter 0.3s ease;
        }


        .logo-wrapper img:hover {

            transform: scale(1.025);

            filter:
                drop-shadow(
                    0 22px 42px
                    rgba(0, 0, 0, 0.48)
                )
                drop-shadow(
                    0 0 26px
                    rgba(200, 169, 107, 0.24)
                );
        }


        /* ====================================================
           HEADER
        ==================================================== */

        .header-box {

            max-width: 980px;

            margin:
                0 auto 30px auto;

            padding:
                0 25px 25px 25px;

            text-align: center;

            border-bottom:
                1px solid
                rgba(200, 169, 107, 0.28);
        }


        .main-title {

            text-align: center;

            font-size:
                clamp(
                    25px,
                    3vw,
                    38px
                );

            line-height: 1.25;

            font-weight: 750;

            color:
                #f7f4ec !important;

            margin:
                0 auto 12px auto;

            letter-spacing:
                -0.45px;

            text-shadow:
                0 3px 15px
                rgba(0, 0, 0, 0.30);
        }


        .title-icon {

            color:
                #c8a96b;

            margin-right:
                8px;
        }


        p.subtitle {

            text-align: center;

            font-size: 15.5px;

            line-height: 1.75;

            color:
                #dce2ea !important;

            margin:
                0 auto;

            max-width: 800px;
        }


        p.subtitle b {

            color:
                #d8bd82 !important;

            font-weight:
                700;
        }


        /* ====================================================
           CHAT CONTAINER
        ==================================================== */

        .chat-container {

            background:
                linear-gradient(
                    145deg,
                    rgba(255, 255, 255, 0.075),
                    rgba(255, 255, 255, 0.035)
                );

            border:
                1px solid
                rgba(255, 255, 255, 0.10);

            border-radius:
                24px;

            padding:
                26px;

            max-height:
                70vh;

            overflow-y:
                auto;

            box-shadow:
                0 20px 50px
                rgba(0, 0, 0, 0.24),

                inset 0 1px 0
                rgba(255, 255, 255, 0.06);

            backdrop-filter:
                blur(10px);
        }


        /* ====================================================
           USER CHAT BUBBLE
        ==================================================== */

        .chat-bubble-user {

            background:
                linear-gradient(
                    135deg,
                    #e9edf3 0%,
                    #d9e0e9 100%
                );

            color:
                #182234;

            padding:
                15px 19px;

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

            max-width:
                78%;

            line-height:
                1.68;

            border:
                1px solid
                rgba(255, 255, 255, 0.75);

            box-shadow:
                0 7px 20px
                rgba(0, 0, 0, 0.18);
        }


        .chat-bubble-user b {

            color:
                #24334c;
        }


        /* ====================================================
           ASSISTANT CHAT BUBBLE
        ==================================================== */

        .chat-bubble-assistant {

            background:
                linear-gradient(
                    145deg,
                    #ffffff 0%,
                    #f5f3ee 100%
                );

            color:
                #202b3d;

            padding:
                17px 21px;

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

            max-width:
                84%;

            line-height:
                1.72;

            border-left:
                4px solid
                #c8a96b;

            box-shadow:
                0 7px 20px
                rgba(0, 0, 0, 0.18);
        }


        .chat-bubble-assistant b {

            color:
                #826b3e;
        }


        .analysis-label {

            color:
                #826b3e;

            font-weight:
                700;
        }


        /* ====================================================
           SIDEBAR
        ==================================================== */

        [data-testid="stSidebar"] {

            background:
                linear-gradient(
                    170deg,
                    #f7f4ec 0%,
                    #ebe7dc 55%,
                    #ded9cb 100%
                );

            color:
                #172033;

            border-right:
                1px solid
                rgba(23, 32, 51, 0.12);

            box-shadow:
                8px 0 30px
                rgba(0, 0, 0, 0.16);
        }


        [data-testid="stSidebar"] * {

            color:
                #172033;
        }


        /* ====================================================
           SIDEBAR HEADER
        ==================================================== */

        .sidebar-header {

            text-align:
                center;

            font-weight:
                800;

            font-size:
                15.5px;

            letter-spacing:
                0.75px;

            margin:
                24px 0 14px 0;

            color:
                #172033 !important;

            padding-bottom:
                12px;

            border-bottom:
                1px solid
                rgba(23, 32, 51, 0.18);
        }


        /* ====================================================
           SIDEBAR EMPTY INFO
        ==================================================== */

        [data-testid="stSidebar"] [data-testid="stAlert"] {

            background:
                rgba(255, 255, 255, 0.52) !important;

            border:
                1px solid
                rgba(23, 32, 51, 0.10) !important;

            border-radius:
                15px !important;

            color:
                #344054 !important;
        }


        /* ====================================================
           SIDEBAR BUTTON
        ==================================================== */

        [data-testid="stSidebar"] button {

            background:
                #172033 !important;

            color:
                #f7f4ec !important;

            font-weight:
                700 !important;

            border-radius:
                12px !important;

            border:
                1px solid
                #172033 !important;

            box-shadow:
                0 5px 14px
                rgba(23, 32, 51, 0.18);

            transition:
                all 0.22s ease !important;
        }


        [data-testid="stSidebar"] button:hover {

            background:
                #c8a96b !important;

            color:
                #172033 !important;

            border:
                1px solid
                #c8a96b !important;

            transform:
                translateY(-1px);

            box-shadow:
                0 8px 20px
                rgba(23, 32, 51, 0.20);
        }


        /* ====================================================
           CHAT INPUT
        ==================================================== */

        [data-testid="stChatInput"] {

            border-radius:
                17px !important;

            background:
                rgba(255, 255, 255, 0.97) !important;

            border:
                1px solid
                rgba(23, 32, 51, 0.13) !important;

            box-shadow:
                0 8px 24px
                rgba(0, 0, 0, 0.14);
        }


        [data-testid="stChatInput"] textarea {

            font-size:
                15px !important;

            color:
                #172033 !important;
        }


        [data-testid="stChatInput"] textarea::placeholder {

            color:
                #7a8494 !important;

            opacity:
                1 !important;
        }


        /* ====================================================
           STREAMLIT INFO / SPINNER
        ==================================================== */

        [data-testid="stAlert"] {

            border-radius:
                13px;
        }


        /* ====================================================
           RESPONSIVE
        ==================================================== */

        @media (max-width: 768px) {

            .block-container {

                padding-left:
                    1rem;

                padding-right:
                    1rem;

                padding-top:
                    1rem;
            }


            .logo-wrapper img {

                width:
                    190px !important;
            }


            .header-box {

                padding-left:
                    5px;

                padding-right:
                    5px;
            }


            .main-title {

                font-size:
                    25px;
            }


            p.subtitle {

                font-size:
                    14px;
            }


            .chat-container {

                padding:
                    14px;
            }


            .chat-bubble-user,
            .chat-bubble-assistant {

                max-width:
                    94%;
            }
        }

        </style>
        """
    ),
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "viewing_history_index" not in st.session_state:
    st.session_state.viewing_history_index = None


# ============================================================
# SIDEBAR
# ============================================================

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
        textwrap.dedent(
            """
            <div class="sidebar-header">
                RIWAYAT PERTANYAAN ANDA
            </div>
            """
        ),
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


# ============================================================
# LOGO
# ============================================================

try:

    st.markdown(
        '<div class="logo-wrapper">',
        unsafe_allow_html=True
    )

    st.image(
        "logo.png",
        width=250
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

except Exception:
    pass


# ============================================================
# HEADER
# ============================================================

st.markdown(
    textwrap.dedent(
        <div class="header-box">

            <div class="main-title">
                Chatbot Kitab Undang-Undang Hukum Pidana (KUHP) Baru
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
    ),
    unsafe_allow_html=True
)


# ============================================================
# AREA CHAT
# ============================================================

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


        # ====================================================
        # USER
        # ====================================================

        if role == "user":

            safe_text = html.escape(
                str(text)
            ).replace(
                "\n",
                "<br>"
            )


            st.markdown(
                textwrap.dedent(
                    f"""
                    <div class="chat-bubble-user">
                        <b>Anda ({html.escape(str(time))})</b>
                        <br>
                        {safe_text}
                    </div>
                    """
                ),
                unsafe_allow_html=True
            )


        # ====================================================
        # ASSISTANT
        # ====================================================

        else:

            # Jawaban assistant sengaja tidak di-escape
            # karena dapat mengandung <br>, <b>, dsb.
            safe_answer = str(text)


            st.markdown(
                textwrap.dedent(
                    f"""
                    <div class="chat-bubble-assistant">
                        <b>
                            Jawaban Chatbot Suhardi
                            ({html.escape(str(time))})
                        </b>

                        <br>

                        {safe_answer}
                    </div>
                    """
                ),
                unsafe_allow_html=True
            )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# INPUT CHAT
# ============================================================

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


        # ----------------------------------------------------
        # SIMPAN PERTANYAAN USER
        # ----------------------------------------------------

        st.session_state.messages.append({

            "role":
                "user",

            "text":
                prompt,

            "time":
                current_time

        })


        st.session_state.pending_prompt = prompt


        st.rerun()


    # ========================================================
    # PROSES PERTANYAAN
    # ========================================================

    if st.session_state.pending_prompt:

        with st.spinner(
            "🔎 Sedang menganalisis dengan Agentic RAG..."
        ):

            try:

                # ------------------------------------------------
                # Ambil seluruh riwayat kecuali pertanyaan terakhir
                # ------------------------------------------------

                conversation_history = (
                    st.session_state.messages[:-1].copy()
                )


                # ------------------------------------------------
                # Konversi text -> content
                # ------------------------------------------------

                history_for_agent = [

                    {
                        "role":
                            msg["role"],

                        "content":
                            msg["text"]
                    }

                    for msg in conversation_history
                ]


                # ------------------------------------------------
                # STATE UNTUK AGENT
                # ------------------------------------------------

                state = {

                    "question":
                        st.session_state.pending_prompt,

                    "history":
                        history_for_agent

                }


                # ------------------------------------------------
                # INVOKE AGENTIC RAG
                # ------------------------------------------------

                result = app.runnable_graph.invoke(
                    state
                )


                # ------------------------------------------------
                # AMBIL HASIL
                # ------------------------------------------------

                answer = result.get(
                    "answer",
                    "Tidak ada jawaban ditemukan."
                )


                reasoning = result.get(
                    "reasoning",
                    ""
                )


                # ------------------------------------------------
                # FORMAT JAWABAN
                # ------------------------------------------------

                if reasoning:

                    response_text = (
                        f"{answer}"
                        f"<br><br>"
                        f'<span class="analysis-label">'
                        f"🧠 Analisis:"
                        f"</span> "
                        f"{reasoning}"
                    )

                else:

                    response_text = answer


            except Exception as e:

                response_text = (
                    f"⚠️ Terjadi kesalahan: "
                    f"{html.escape(str(e))}"
                )


        # ========================================================
        # WAKTU JAWABAN
        # ========================================================

        tz = pytz.timezone(
            "Asia/Jakarta"
        )


        current_time = datetime.datetime.now(
            tz
        ).strftime("%H:%M:%S")


        # ========================================================
        # SIMPAN JAWABAN
        # ========================================================

        st.session_state.messages.append({

            "role":
                "assistant",

            "text":
                response_text,

            "time":
                current_time

        })


        st.session_state.pending_prompt = None


        st.rerun()


# ============================================================
# MODE MELIHAT HISTORY
# ============================================================

else:

    st.info(
        "🔒 Anda sedang melihat riwayat chat lama. "
        "Klik 'MULAI CHAT BARU' untuk memulai percakapan baru."
    )
