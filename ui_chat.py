import streamlit as st
import datetime
import pytz
import app
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
# CSS (raw string)
# ============================================================

st.markdown(
    r"""
    <style>

    /* ========================================================
       GLOBAL
    ======================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 50% -15%,
                rgba(148, 163, 184, 0.14),
                transparent 38%
            ),
            linear-gradient(
                145deg,
                #0b1220 0%,
                #111827 50%,
                #1e293b 100%
            );

        color: #f8fafc;
        font-family:
            "Segoe UI",
            "Inter",
            Arial,
            sans-serif;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }

    /* ========================================================
       HEADER AREA
    ======================================================== */

    .header-divider {
        height: 1px;
        width: 100%;
        margin-top: 24px;
        margin-bottom: 28px;

        background:
            linear-gradient(
                90deg,
                transparent,
                rgba(148, 163, 184, 0.30),
                transparent
            );
    }


    /* ========================================================
       SIDEBAR
    ======================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                165deg,
                #f8fafc 0%,
                #e2e8f0 100%
            );

        border-right:
            1px solid rgba(15, 23, 42, 0.10);
        box-shadow:
            8px 0 30px rgba(0, 0, 0, 0.14);
    }

    [data-testid="stSidebar"] * {
        color: #1e293b;
    }

    .sidebar-title {
        text-align: center;
        font-size: 15px;
        font-weight: 800;
        letter-spacing: 0.8px;
        color: #172033;
        margin-top: 24px;
        margin-bottom: 15px;
        padding-bottom: 12px;
        border-bottom:
            1px solid rgba(71, 85, 105, 0.22);
    }

    [data-testid="stSidebar"] button {
        background: #ffffff !important;
        color: #7f1d1d !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border:
            1px solid rgba(127, 29, 29, 0.28) !important;
        box-shadow:
            0 4px 12px rgba(15, 23, 42, 0.08);
        transition:
            all 0.2s ease !important;
    }

    [data-testid="stSidebar"] button:hover {
        background: #7f1d1d !important;
        color: #ffffff !important;
        border-color: #7f1d1d !important;
        transform: translateY(-1px);
        box-shadow:
            0 7px 18px rgba(127, 29, 29, 0.22);
    }

    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background:
            rgba(255, 255, 255, 0.75);
        border:
            1px solid rgba(71, 85, 105, 0.15);
        border-radius: 13px;
        color: #475569;
    }

    /* ========================================================
       CHAT CONTAINER
    ======================================================== */

    .chat-panel {
        background:
            rgba(255, 255, 255, 0.045);
        border:
            1px solid rgba(255, 255, 255, 0.08);
        border-radius: 22px;
        padding: 18px 20px;
        box-shadow:
            0 20px 50px rgba(0, 0, 0, 0.22),
            inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    /* ========================================================
       CHAT MESSAGE BOX - MERAH TERANG MENYALA ESTETIK
    ======================================================== */

    [data-testid="stChatMessage"] {
        background: linear-gradient(145deg, #ff0040, #cc0033) !important;
        border: 1px solid rgba(255, 0, 64, 0.7) !important;
        box-shadow:
            0 0 25px rgba(255, 0, 64, 0.6),
            inset 0 0 15px rgba(255, 255, 255, 0.15) !important;
        border-radius: 18px !important;
        padding: 10px 16px !important;
        margin-bottom: 14px !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stChatMessage"]:hover {
        box-shadow:
            0 0 40px rgba(255, 0, 64, 0.9),
            inset 0 0 20px rgba(255, 255, 255, 0.25) !important;
        transform: scale(1.01);
    }

    /* ========================================================
       CHAT MESSAGE TEXT COLOR - PUTIH (kecuali caption)
    ======================================================== */

    /* Semua teks di dalam chat message menjadi putih (default) */
    [data-testid="stChatMessage"] * {
        color: #ffffff !important;
    }

    /* ========================================================
       CAPTION KHUSUS - HITAM TERANG, BOLD, BESAR
       Menggunakan kelas .custom-caption yang kita buat sendiri
    ======================================================== */

    .custom-caption {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 0.95em !important;
        text-shadow: 0 0 12px rgba(255, 255, 255, 0.95) !important;
        margin-bottom: 4px !important;
    }


    /* ========================================================
       EXPANDER (Analisis) - KOTAK HIJAU TERANG MENYALA
       dan teks hitam menyala
    ======================================================== */

    /* Kotak expander (saat terbuka) */
    [data-testid="stExpander"] details {
        background: linear-gradient(145deg, #00ff44, #00cc33) !important;
        border: 2px solid rgba(0, 255, 68, 0.9) !important;
        box-shadow:
            0 0 30px rgba(0, 255, 68, 0.7),
            inset 0 0 20px rgba(255, 255, 255, 0.3) !important;
        border-radius: 15px !important;
        padding: 10px !important;
    }

    /* Judul expander (summary) - hitam menyala */
    [data-testid="stExpander"] summary {
        color: #000000 !important;
        text-shadow:
            0 0 5px rgba(0, 0, 0, 0.8),
            0 0 10px rgba(0, 255, 68, 0.5) !important;
        font-weight: bold !important;
        font-size: 1.1em !important;
    }

    /* Semua teks di dalam expander (termasuk analisis) menjadi hitam */
    [data-testid="stExpander"] details * {
        color: #000000 !important;
        text-shadow:
            0 0 5px rgba(255, 255, 255, 0.3),
            0 0 10px rgba(0, 255, 68, 0.4) !important;
    }

    /* Khusus untuk markdown di dalam expander agar hitam */
    [data-testid="stExpander"] .stMarkdown {
        color: #000000 !important;
    }


    /* ========================================================
       NATIVE STREAMLIT CHAT MESSAGE (overrides tambahan)
    ======================================================== */

    [data-testid="stChatMessage"] {
        border-radius: 18px;
        padding: 8px 14px;
        margin-bottom: 12px;
    }

    /* ========================================================
       CHAT INPUT
    ======================================================== */

    [data-testid="stChatInput"] {
        margin-top: 15px;
    }
    
    [data-testid="stChatInput"] > div {
        background: #f8fafc !important;
        border:
            1px solid rgba(148, 163, 184, 0.35) !important;
        border-radius: 17px !important;
        box-shadow:
            0 10px 28px rgba(0, 0, 0, 0.18) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #1e293b !important;
        font-size: 15px !important;
    }

    /* ========================================================
       INFO
    ======================================================== */

    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* ========================================================
       MOBILE
    ======================================================== */

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
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

    # --------------------------------------------------------
    # CHAT BARU
    # --------------------------------------------------------

    if st.button(
        "MULAI CHAT BARU",
        use_container_width=True
    ):

        # Simpan riwayat saat ini jika ada pesan
        if st.session_state.messages:
            if st.session_state.viewing_history_index is not None:
                # Perbarui riwayat yang sedang dilihat
                st.session_state.chat_history[st.session_state.viewing_history_index] = st.session_state.messages.copy()
            else:
                # Tambahkan sebagai riwayat baru
                st.session_state.chat_history.append(st.session_state.messages.copy())

        # Reset ke chat baru
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.session_state.viewing_history_index = None

        st.rerun()

    # --------------------------------------------------------
    # HEADER RIWAYAT
    # --------------------------------------------------------

    st.markdown(
        '<div class="sidebar-title">RIWAYAT PERTANYAAN ANDA</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------------------------
    # RIWAYAT
    # --------------------------------------------------------

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
                # Muat riwayat ke sesi saat ini
                st.session_state.messages = chat.copy()
                st.session_state.viewing_history_index = (
                    len(st.session_state.chat_history) - i)
                st.session_state.pending_prompt = None
                st.rerun()

    else:

        st.info(
            'Belum ada riwayat pertanyaan tersimpan. '
            'Riwayat akan tersimpan setelah Anda menekan '
            '"MULAI CHAT BARU".'
        )

# ============================================================
# HEADER UTAMA
# ============================================================

logo_col, text_col = st.columns(
    [1.5, 3.5],
    vertical_alignment="center"
)

# ============================================================
# LOGO
# ============================================================

with logo_col:
    try:
        st.image(
            "logo.png",
            width=700
        )
    except Exception:
        st.markdown(
            "⚖️",
            unsafe_allow_html=False
        )

# ============================================================
# TEKS DI SAMPING LOGO (rata tengah & putih)
# ============================================================

with text_col:
    st.markdown(
        """
        <div style="text-align: center; color: #ffffff;">
            <h1>Asisten Cerdas Kitab Undang-Undang Hukum Pidana (KUHP) Baru</h1>
            <h3>Agentic RAG with LangChain</h3>
            <p>Tanyakan apa pun seputar <strong>UU No. 1 Tahun 2023 tentang KUHP</strong>.</p>
            <p>Chatbot ini dibuat oleh <strong>SUHARDI</strong>.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================
# GARIS PEMISAH HEADER
# ============================================================

st.markdown(
    '<div class="header-divider"></div>',
    unsafe_allow_html=True
)

# ============================================================
# AREA CHAT
# ============================================================

chat_panel = st.container()

with chat_panel:
    if st.session_state.messages:
        for msg in st.session_state.messages:
            role = msg["role"]
            text = str(msg["text"])
            time = msg["time"]

            # =================================================
            # USER
            # =================================================

            if role == "user":
                with st.chat_message(
                    "user",
                    avatar="👤"
                ):
                    st.markdown(
                        f'<div class="custom-caption">Anda • {time}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(text)

            # =================================================
            # ASSISTANT
            # =================================================

            else:
                with st.chat_message(
                    "assistant",
                    avatar="⚖️"
                ):
                    st.markdown(
                        f'<div class="custom-caption">Chatbot Suhardi • {time}</div>',
                        unsafe_allow_html=True
                    )

                    # -----------------------------------------
                    # Bersihkan HTML
                    # -----------------------------------------

                    clean_text = (
                        text
                        .replace("<br><br>", "\n\n")
                        .replace("<br>", "\n")
                        .replace("<br/>", "\n")
                        .replace("<br />", "\n")
                        .replace("<b>", "**")
                        .replace("</b>", "**")
                        .replace("<strong>", "**")
                        .replace("</strong>", "**")
                    )

                    # -----------------------------------------
                    # Jika terdapat analisis
                    # -----------------------------------------
                    
                    analysis_marker = (
                        "🧠 **Analisis:**"
                    )

                    if analysis_marker in clean_text:
                        answer_part, reasoning_part = (
                            clean_text.split(
                                analysis_marker,
                                1
                            )
                        )
                        st.markdown(
                            answer_part.strip()
                        )
                        with st.expander(
                            "🧠 Analisis",
                            expanded=False
                        ):
                            st.markdown(
                                reasoning_part.strip()
                            )
                    else:
                        st.markdown(
                            clean_text
                        )

# ============================================================
# NOTIFIKASI RIWAYAT (jika sedang melihat)
# ============================================================

if st.session_state.viewing_history_index is not None:
    st.info(
        "🔒 Anda sedang melihat riwayat chat lama. "
        "Anda dapat melanjutkan percakapan di bawah ini. "
        "Klik 'MULAI CHAT BARU' untuk memulai percakapan baru."
    )

# ============================================================
# INPUT CHAT & PROSES RAG
# ============================================================

prompt = st.chat_input(
    "💬 Tuliskan pertanyaan Anda seputar KUHP Baru..."
)

# ============================================================
# PERTANYAAN BARU
# ============================================================

if prompt:
    tz = pytz.timezone("Asia/Jakarta")
    current_time = datetime.datetime.now(
        tz
    ).strftime("%H:%M:%S")

    # ----------------------------------------------------
    # Simpan pertanyaan user
    # ----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "text": prompt,
            "time": current_time
        }
    )
    st.session_state.pending_prompt = prompt
    st.rerun()

# ============================================================
# PROSES AGENTIC RAG
# ============================================================

if st.session_state.pending_prompt:
    with st.spinner(
        "🔍 Sedang menganalisis dengan Agentic RAG..."):
        try:
            # ------------------------------------------------
            # Ambil seluruh percakapan sebelum pertanyaan
            # terakhir.
            # ------------------------------------------------
            conversation_history = (
                st.session_state.messages[:-1].copy()
            )
            # ------------------------------------------------
            # Format history untuk agent
            # ------------------------------------------------
            history_for_agent = [
                {
                    "role": msg["role"],
                    "content": msg["text"]
                }
                for msg in conversation_history
            ]
            # ------------------------------------------------
            # State
            # ------------------------------------------------
            state = {
                "question":
                    st.session_state.pending_prompt,
                "history":
                    history_for_agent
            }
            # ------------------------------------------------
            # Jalankan graph
            # ------------------------------------------------

            result = app.runnable_graph.invoke(state)

            # ------------------------------------------------
            # Ambil jawaban
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
            # Simpan jawaban
            # ------------------------------------------------

            if reasoning:
                response_text = (
                    f"{answer}\n\n"
                    f"🧠 **Analisis:**\n"
                    f"{reasoning}"
                )
            else:
                response_text = str(
                    answer
                )
        except Exception as e:
            response_text = (
                "⚠️ Terjadi kesalahan:\n\n"
                f"{str(e)}"
            )

    # ========================================================
    # WAKTU RESPONSE
    # ========================================================

    tz = pytz.timezone("Asia/Jakarta")

    current_time = datetime.datetime.now(
        tz
    ).strftime("%H:%M:%S")

    # ========================================================
    # SIMPAN RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "text": response_text,
            "time": current_time
        }
    )

    # ========================================================
    # PERBARUI RIWAYAT jika sedang melihat
    # ========================================================

    if st.session_state.viewing_history_index is not None:
        st.session_state.chat_history[st.session_state.viewing_history_index] = st.session_state.messages.copy()

    st.session_state.pending_prompt = None
    st.rerun()
