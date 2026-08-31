# ⚖️ Agentic RAG KUHP Baru

### AI-Powered Legal Assistant untuk Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana

<p align="center">
  <img src="assets/logo.png" alt="Agentic RAG KUHP Baru Logo" width="737">
</p>

<p align="center">
  <strong>AI for Equal Justice</strong><br>
  Asisten hukum berbasis Agentic Retrieval-Augmented Generation (Agentic RAG)
  untuk membantu memahami KUHP Baru secara lebih mudah, kontekstual, dan berbasis sumber.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red)
![LangChain](https://img.shields.io/badge/LangChain-Framework-green)
![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Workflow-purple)
![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM%20Gateway-orange)
![Tavily](https://img.shields.io/badge/Tavily-Web%20Search-blue)
![RAG](https://img.shields.io/badge/Architecture-Agentic%20RAG-orange)

</p>

---

## 📌 Tentang Proyek

**Agentic RAG KUHP Baru** merupakan aplikasi asisten hukum berbasis **Artificial Intelligence (AI)** yang dirancang untuk membantu masyarakat memperoleh informasi dan memahami ketentuan dalam **Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana (KUHP Baru)**.

Proyek ini mengimplementasikan pendekatan **Agentic Retrieval-Augmented Generation (Agentic RAG)** yang mengombinasikan kemampuan **Large Language Model (LLM)**, retrieval dokumen hukum, workflow agen berbasis **LangGraph**, serta berbagai sumber informasi pendukung.

Berbeda dari sistem pencarian berbasis kata kunci sederhana, agen dirancang untuk memahami konteks pertanyaan, menentukan informasi yang dibutuhkan, melakukan retrieval terhadap sumber yang relevan, mengevaluasi kecukupan informasi, dan menghasilkan jawaban berdasarkan konteks yang diperoleh.

Sistem juga dilengkapi dengan **conversation memory**, sehingga konteks pertanyaan sebelumnya dapat dipertahankan selama sesi percakapan. Hal tersebut memungkinkan pengguna mengajukan pertanyaan lanjutan tanpa harus mengulangi seluruh konteks pembicaraan.

> **AI for Equal Justice** — teknologi AI dimanfaatkan sebagai sarana pendukung untuk memperluas akses terhadap informasi hukum yang akurat, transparan, dan mudah dipahami.

---

## 🎯 Latar Belakang

Perkembangan kecerdasan buatan telah membuka peluang baru dalam penyediaan layanan informasi di berbagai bidang, termasuk bidang hukum.

Di Indonesia, kebutuhan terhadap akses informasi hukum semakin relevan setelah diberlakukannya **Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana (KUHP Baru)**.

KUHP Baru memiliki struktur dan substansi yang kompleks serta memuat **624 pasal**. Bagi masyarakat yang tidak memiliki latar belakang hukum, memahami keseluruhan ketentuan tersebut dapat menjadi tantangan.

Permasalahan semakin kompleks ketika pencarian informasi hukum dilakukan menggunakan sistem berbasis keyword search. Pencarian berbasis kata kunci dapat menemukan dokumen yang mengandung istilah tertentu, tetapi belum tentu memahami:

* konteks pertanyaan;
* maksud pengguna;
* hubungan antarketentuan;
* konsep hukum yang sedang ditanyakan;
* informasi apa yang sebenarnya dibutuhkan;
* serta bagaimana menjelaskan ketentuan hukum dalam bahasa yang mudah dipahami.

Di sisi lain, penggunaan LLM tanpa sumber eksternal atau mekanisme retrieval memiliki risiko **hallucination**, yaitu menghasilkan informasi yang terdengar meyakinkan tetapi tidak memiliki dasar yang benar.

Oleh karena itu, proyek ini mengadopsi pendekatan **Agentic RAG** untuk menggabungkan kemampuan reasoning LLM dengan retrieval terhadap sumber hukum.

---

# ❗ Problem Statement

### Permasalahan Utama

Terdapat beberapa permasalahan yang ingin diselesaikan melalui proyek ini:

1. **Kompleksitas KUHP Baru**

   KUHP Baru terdiri dari 624 pasal sehingga membutuhkan waktu dan ketelitian untuk dipelajari secara menyeluruh.

2. **Kesulitan masyarakat memahami bahasa hukum**

   Istilah dan struktur bahasa hukum sering kali sulit dipahami oleh masyarakat yang tidak memiliki latar belakang hukum.

3. **Keterbatasan keyword search**

   Sistem pencarian konvensional cenderung berorientasi pada kecocokan kata, bukan pemahaman terhadap konteks pertanyaan.

4. **Keterbatasan LLM tanpa retrieval**

   LLM dapat menghasilkan jawaban yang tidak memiliki dasar hukum yang memadai apabila tidak diberikan sumber informasi yang relevan.

5. **Kebutuhan terhadap informasi hukum yang dapat ditelusuri**

   Jawaban hukum idealnya dapat dikaitkan kembali dengan sumber hukum yang menjadi dasar informasi tersebut.

### Solusi yang Ditawarkan

Proyek ini menggunakan pendekatan **Agentic Retrieval-Augmented Generation** sehingga sistem dapat:

```text
User Question
      │
      ▼
Context & Intent Analysis
      │
      ▼
Source Selection
      │
      ├───────────────┐
      ▼               ▼
KUHP Baru        External Sources
      │               │
      └───────┬───────┘
              ▼
          Information
           Synthesis
              │
              ▼
        Answer Evaluation
              │
       ┌──────┴──────┐
       │             │
    Sufficient    Insufficient
       │             │
       ▼             └──────► Retrieval
    Final Answer
```

Dengan demikian, sistem tidak hanya berfungsi sebagai chatbot, tetapi sebagai **agen yang dapat menentukan langkah yang diperlukan untuk menghasilkan jawaban**.

---

# 👥 Target Pengguna

Aplikasi dirancang untuk berbagai kelompok pengguna.

### 👤 Masyarakat Umum

Membantu memperoleh pemahaman awal mengenai ketentuan KUHP Baru tanpa harus memahami terminologi hukum secara mendalam.

### 🎓 Mahasiswa dan Pelajar

Dapat digunakan sebagai media pembelajaran interaktif untuk mengeksplorasi konsep, pasal, serta hubungan antarketentuan dalam KUHP Baru.

### 🔬 Akademisi dan Peneliti

Mendukung proses eksplorasi dan penelusuran informasi hukum dalam kegiatan akademik dan penelitian.

### ⚖️ Praktisi Hukum

Dapat digunakan sebagai alat bantu pencarian awal terhadap referensi hukum.

### 🏛️ Instansi Pemerintah dan Pelayanan Publik

Berpotensi digunakan sebagai pendukung penyediaan informasi hukum kepada masyarakat.

---

# ✨ Fitur Utama

### 🤖 Agentic RAG

Menggunakan workflow agen untuk menentukan langkah retrieval dan reasoning secara adaptif.

### 📚 KUHP sebagai Knowledge Base Utama

Dokumen `KUHP_Baru.txt` digunakan sebagai sumber pengetahuan utama sistem.

### 🧠 LLM Reasoning

LLM digunakan untuk memahami pertanyaan, mengintegrasikan informasi, serta menyusun jawaban berdasarkan konteks.

### 🔎 Multi-Source Retrieval

Sistem dapat memanfaatkan sumber informasi internal maupun eksternal sesuai kebutuhan.

### 💬 Conversation Memory

Konteks percakapan dipertahankan selama sesi sehingga pengguna dapat mengajukan pertanyaan lanjutan secara natural.

### 🔄 Iterative Retrieval

Apabila informasi yang diperoleh belum memadai, workflow dapat kembali melakukan retrieval untuk memperoleh informasi tambahan.

### 📖 Source-Grounded Answer

Jawaban diarahkan agar tetap berlandaskan sumber informasi yang digunakan dalam proses retrieval.

### 📊 Observability

Proses workflow agen dapat dipantau selama pengembangan dan evaluasi menggunakan LangSmith.

---

# 🏗️ Arsitektur Sistem

Secara konseptual, arsitektur sistem terdiri atas beberapa lapisan:

```text
┌─────────────────────────────────────┐
│              USER                   │
│         Legal Question              │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│            STREAMLIT                │
│         User Interface              │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│            LANGGRAPH                │
│          Agent Workflow             │
│                                     │
│  ┌────────────┐   ┌─────────────┐  │
│  │   Query    │──►│   Source    │  │
│  │ Analysis   │   │  Selection  │  │
│  └────────────┘   └──────┬──────┘  │
│                          │         │
│                          ▼         │
│                   ┌─────────────┐ │
│                   │  Retrieval  │ │
│                   └──────┬──────┘ │
│                          │         │
│                          ▼         │
│                   ┌─────────────┐ │
│                   │ Evaluation  │ │
│                   └──────┬──────┘ │
└──────────────────────────┼─────────┘
                           │
                           ▼
┌─────────────────────────────────────┐
│              LLM                    │
│        Reasoning & Generation       │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         FINAL RESPONSE              │
│   Explanation + Legal References   │
└─────────────────────────────────────┘
```

---

# 🧩 Technology Stack

| Komponen             | Teknologi              | Fungsi                             |
| -------------------- | ---------------------- | ---------------------------------- |
| Programming Language | Python                 | Pengembangan aplikasi              |
| UI                   | Streamlit              | Antarmuka pengguna                 |
| Agent Framework      | LangGraph              | Workflow dan state management agen |
| LLM Orchestration    | LangChain              | Integrasi LLM dan tools            |
| LLM Gateway          | OpenRouter             | Akses model bahasa                 |
| LLM                  | Cohere North Mini Code | Reasoning dan generation           |
| Knowledge Base       | `KUHP_Baru.txt`        | Sumber hukum utama                 |
| Search               | Tavily                 | Pencarian informasi eksternal      |
| Knowledge Source     | Wikipedia              | Informasi konseptual               |
| Academic Source      | arXiv                  | Referensi akademik                 |
| Observability        | LangSmith              | Monitoring dan tracing             |
| Deployment           | Streamlit Cloud        | Hosting aplikasi                   |

> **Catatan:** model LLM dapat diganti dengan model lain sesuai kebutuhan, termasuk model premium dengan kapasitas konteks dan kemampuan yang lebih besar.

---

# 📚 Knowledge Base

Sumber pengetahuan utama aplikasi adalah:

```text
KUHP_Baru.txt
```

Dokumen tersebut berisi teks **Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana** yang digunakan sebagai basis informasi utama dalam proses retrieval.

Prioritas terhadap dokumen hukum utama dimaksudkan agar jawaban yang berkaitan langsung dengan substansi KUHP tetap memiliki landasan hukum yang jelas.

Sumber eksternal digunakan sebagai informasi pendukung ketika dibutuhkan, bukan sebagai pengganti sumber hukum utama.

---

# 🔎 Retrieval & External Tools

Sistem dapat menggunakan beberapa sumber informasi pendukung.

### Wikipedia

Digunakan untuk membantu memperoleh informasi konseptual mengenai istilah atau konsep tertentu.

### arXiv

Digunakan untuk memperoleh referensi akademik yang relevan.

### Tavily Search

Digunakan untuk memperoleh informasi eksternal dan informasi yang membutuhkan pencarian web.

### KUHP Baru

Merupakan **knowledge source utama** untuk pertanyaan yang berkaitan dengan substansi KUHP.

---

# 🧠 Agentic Workflow

Salah satu karakteristik utama proyek ini adalah penggunaan workflow agen.

Secara umum, proses dapat digambarkan sebagai:

```text
                User Question
                     │
                     ▼
              Query Analysis
                     │
                     ▼
             Source Selection
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
     KUHP Retrieval       External Search
          │                     │
          └──────────┬──────────┘
                     ▼
              Context Assembly
                     │
                     ▼
                LLM Reasoning
                     │
                     ▼
               Answer Review
                     │
              ┌──────┴──────┐
              │             │
          Adequate       Inadequate
              │             │
              ▼             ▼
        Final Answer     Retrieval
```

Pendekatan tersebut memungkinkan sistem melakukan proses secara iteratif dibandingkan pipeline RAG sederhana yang selalu mengikuti satu jalur tetap.

---

# 💬 Conversation Memory

Aplikasi mendukung percakapan multi-turn.

Contohnya:

```text
User:
Apa yang dimaksud dengan tindak pidana?

Agent:
[Tanggapan mengenai tindak pidana]

User:
Bagaimana dengan bentuk pertanggungjawabannya?

Agent:
[Jawaban menggunakan konteks percakapan sebelumnya]
```

Dengan mekanisme tersebut, pengguna tidak selalu perlu mengulang konteks pada setiap pertanyaan.

Conversation memory sangat berguna ketika pengguna melakukan eksplorasi hukum secara bertahap.

---

# 🖥️ Tampilan Aplikasi

![Screenshot Aplikasi](assets/Screenshot.png)

Antarmuka aplikasi dirancang agar pengguna dapat melakukan interaksi dengan agen melalui percakapan secara langsung.

---

# 📂 Struktur Repository

```text
Agentic-RAG-KUHP-Baru/
│
├── Assets/
│   ├── logo.png
│   └── screenshot.png
│
├── KUHP_Baru.txt
│
├── app.py
│
├── ui_chat.py
│
├── requirements.txt
│
└── README.md
```

### Penjelasan

| File / Folder           | Fungsi                   |
| ----------------------- | ------------------------ |
| `Assets/`               | Asset visual aplikasi    |
| `Assets/logo.png`       | Logo aplikasi            |
| `Assets/screenshot.png` | Screenshot antarmuka     |
| `KUHP_Baru.txt`         | Knowledge base KUHP Baru |
| `app.py`                | Komponen utama aplikasi  |
| `ui_chat.py`            | Komponen antarmuka chat  |
| `requirements.txt`      | Dependencies Python      |
| `README.md`             | Dokumentasi proyek       |

---

# ⚙️ Requirements

Pastikan sistem memiliki:

* Python 3.x
* pip
* Git
* Internet connection
* API key untuk layanan yang digunakan

Dependencies Python tersedia pada:

```text
requirements.txt
```

---

# 🚀 Installation

Clone repository:

```bash
git clone https://github.com/dkasi059-dev/Agentic-RAG-KUHP-Baru.git
```

Masuk ke directory:

```bash
cd Agentic-RAG-KUHP-Baru
```

Buat virtual environment:

```bash
python -m venv venv
```

Aktifkan virtual environment.

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Buat file:

```text
.env
```

Kemudian masukkan API key yang diperlukan sesuai konfigurasi aplikasi.

Contoh:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
TAVILY_API_KEY=your_tavily_api_key
LANGCHAIN_API_KEY=your_langsmith_api_key
```

> **Penting:** jangan pernah melakukan commit terhadap `.env` yang berisi API key asli.

Gunakan `.gitignore` untuk mencegah file tersebut masuk ke repository.

Contoh:

```text
.env
venv/
__pycache__/
*.pyc
```

---

# ▶️ Menjalankan Aplikasi

Setelah dependencies dan environment variables dikonfigurasi, jalankan:

```bash
streamlit run app.py
```

Streamlit kemudian akan menjalankan aplikasi pada server lokal.

---

# ☁️ Deployment

Aplikasi dapat di-deploy menggunakan **Streamlit Cloud**.

Secara umum proses deployment:

```text
GitHub Repository
       │
       ▼
Streamlit Cloud
       │
       ▼
Configure Secrets
       │
       ▼
Deploy
       │
       ▼
Web Application
```

API key sebaiknya disimpan menggunakan **Secrets** pada platform deployment dan tidak dimasukkan langsung ke source code.

---

# 📊 Observability

Selama pengembangan, sistem dapat menggunakan **LangSmith** untuk melakukan observability terhadap workflow agen.

Monitoring dapat membantu melihat:

* input pengguna;
* proses reasoning;
* node yang dijalankan;
* pemanggilan tools;
* retrieval;
* output LLM;
* latency;
* penggunaan token;
* serta error yang terjadi selama workflow.

Observability menjadi penting dalam pengembangan Agentic RAG karena workflow tidak hanya terdiri dari satu pemanggilan model.

---

# ⚠️ Limitations

Proyek ini memiliki beberapa keterbatasan.

### 1. Bukan Pengganti Konsultasi Hukum

Aplikasi merupakan **alat bantu informasi**, bukan pengganti advokat, konsultan hukum, hakim, jaksa, maupun profesional hukum lainnya.

### 2. Potensi Hallucination

Meskipun Agentic RAG dirancang untuk mengurangi hallucination melalui retrieval dan evaluasi, sistem berbasis LLM tetap memiliki kemungkinan menghasilkan informasi yang tidak sempurna.

### 3. Ketergantungan terhadap Sumber

Kualitas jawaban sangat dipengaruhi oleh kualitas dan kelengkapan sumber yang tersedia.

### 4. Keterbatasan Model

Model gratis atau model dengan kapasitas tertentu dapat memiliki keterbatasan context window, rate limit, reasoning capability, maupun jumlah pemanggilan.

### 5. Ruang Lingkup Knowledge Base

Implementasi saat ini berfokus pada **KUHP Baru**. Regulasi lain yang berkaitan belum seluruhnya menjadi bagian dari knowledge base utama.

Karena itu, informasi yang dihasilkan sebaiknya tetap diverifikasi terhadap dokumen hukum resmi.

---

# 🔒 Responsible AI

Karena aplikasi berada dalam domain hukum, penggunaan AI perlu dilakukan secara bertanggung jawab.

Prinsip yang digunakan dalam proyek ini meliputi:

* mengutamakan sumber hukum sebagai landasan;
* membedakan informasi hukum dari interpretasi AI;
* tidak memosisikan AI sebagai pengganti profesional hukum;
* mendorong verifikasi terhadap sumber resmi;
* menjaga kerahasiaan API credentials;
* serta menyadari keterbatasan model generatif.

Tujuan utama sistem adalah **mempermudah akses terhadap informasi hukum**, bukan memberikan keputusan hukum yang mengikat.

---

# 🌱 Impact

Teknologi AI memiliki potensi untuk membantu mengurangi hambatan akses terhadap informasi hukum.

Melalui aplikasi ini, pengguna dapat memperoleh sarana untuk:

* memahami konsep hukum;
* mencari ketentuan dalam KUHP Baru;
* mengeksplorasi pertanyaan hukum secara conversational;
* menemukan informasi yang relevan dengan lebih cepat;
* serta memahami informasi hukum dengan bahasa yang lebih mudah dicerna.

Dampak yang diharapkan tidak hanya bersifat teknis, tetapi juga sosial melalui peningkatan **literasi hukum** dan akses terhadap informasi.

---

# 🔮 Future Development

Pengembangan selanjutnya dapat diarahkan pada beberapa aspek.

### 🗄️ Vector Database

Mengintegrasikan vector database untuk memungkinkan semantic retrieval yang lebih efisien ketika jumlah dokumen semakin besar.

### 📚 Multi-Regulation Knowledge Base

Memperluas knowledge base dari KUHP menjadi berbagai regulasi lain, seperti:

* KUHAP;
* KUHPerdata;
* peraturan pemerintah;
* peraturan sektoral;
* serta regulasi nasional lainnya.

### 🔗 Cross-Regulation Reasoning

Memungkinkan agen menganalisis keterkaitan antara beberapa peraturan dalam satu proses reasoning.

### 📑 Structured Legal Citation

Mengembangkan mekanisme sitasi pasal secara lebih terstruktur sehingga pengguna dapat mengetahui dasar hukum dari setiap bagian jawaban.

### 🕸️ Legal Knowledge Graph

Membangun representasi hubungan:

```text
Pasal
 │
 ├── Unsur Tindak Pidana
 │
 ├── Sanksi
 │
 ├── Pengecualian
 │
 └── Pasal Terkait
```

sehingga hubungan antar ketentuan dapat dieksplorasi secara visual.

### 🧠 Improved Reasoning

Menggunakan model yang lebih kuat untuk meningkatkan kemampuan reasoning, terutama untuk pertanyaan hukum yang membutuhkan analisis multi-step.

### 📈 Automated Evaluation

Menambahkan framework evaluasi khusus RAG untuk mengukur:

* faithfulness;
* answer relevancy;
* context precision;
* context recall;
* retrieval quality;
* latency;
* token usage;
* dan cost.

---

# 🗺️ Roadmap

```text
[x] KUHP Baru sebagai knowledge base
[x] LLM integration
[x] Agentic workflow
[x] Streamlit interface
[x] Conversation memory
[x] External information sources
[x] LangSmith observability
[ ] Vector database
[ ] Structured legal citation
[ ] Multi-regulation retrieval
[ ] Legal knowledge graph
[ ] Automated RAG evaluation
[ ] Production-scale deployment
```

---

# 📖 Use Case Example

Contoh interaksi:

```text
User:
Apa yang dimaksud dengan tindak pidana dalam KUHP Baru?

        ↓

Agent
        ↓

Menganalisis pertanyaan
        ↓

Melakukan retrieval
        ↓

Mengambil konteks dari KUHP Baru
        ↓

Menganalisis informasi
        ↓

Mengevaluasi kecukupan konteks
        ↓

Menghasilkan jawaban
        ↓

User menerima penjelasan
```

Pengguna kemudian dapat melanjutkan:

```text
User:
Apa unsur-unsurnya?

Agent:
Mempertahankan konteks percakapan sebelumnya
dan memberikan jawaban lanjutan.
```

---

# 🧪 Evaluation

Evaluasi sistem dapat dilakukan dari beberapa dimensi.

### Retrieval

Mengukur apakah sistem mampu menemukan konteks hukum yang relevan.

### Generation

Mengukur apakah jawaban yang dihasilkan sesuai dengan konteks yang diperoleh.

### Faithfulness

Mengukur apakah jawaban tetap berlandaskan informasi yang tersedia.

### Relevance

Mengukur apakah jawaban benar-benar menjawab pertanyaan pengguna.

### Agent Workflow

Mengukur kemampuan agen dalam menentukan sumber dan langkah retrieval yang sesuai.

### Performance

Mengukur:

* response latency;
* token consumption;
* API usage;
* dan biaya inference.

Evaluasi yang lebih komprehensif dapat ditambahkan pada pengembangan berikutnya.

---

# 🤝 Contributing

Kontribusi terhadap proyek sangat terbuka.

Jika ingin berkontribusi:

```bash
git clone https://github.com/dkasi059-dev/Agentic-RAG-KUHP-Baru.git
```

Buat branch:

```bash
git checkout -b feature/nama-fitur
```

Lakukan perubahan dan commit:

```bash
git add .
git commit -m "Add new feature"
```

Push branch:

```bash
git push origin feature/nama-fitur
```

Kemudian buat Pull Request.

---

# 📜 License

Jika repository menggunakan lisensi MIT, sertakan file `LICENSE` pada root repository dan gunakan:

```text
This project is licensed under the MIT License.
```

Sesuaikan bagian ini apabila repository menggunakan lisensi yang berbeda.

---

# 👨‍💻 Project

**Agentic RAG KUHP Baru**

**AI for Equal Justice**

Repository:

https://github.com/dkasi059-dev/Agentic-RAG-KUHP-Baru

---

# 📚 References

1. Undang-Undang Republik Indonesia Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana.
2. Dokumentasi LangChain.
3. Dokumentasi LangGraph.
4. Dokumentasi Streamlit.
5. Dokumentasi OpenRouter.
6. Dokumentasi Tavily.
7. Dokumentasi LangSmith.
8. Dokumentasi Wikipedia API.
9. Dokumentasi arXiv.

---

## ⚖️ Disclaimer

**Agentic RAG KUHP Baru merupakan sistem berbasis kecerdasan buatan untuk membantu akses dan pemahaman awal terhadap informasi hukum. Sistem ini bukan merupakan pengganti konsultasi hukum profesional dan tidak memberikan nasihat hukum yang mengikat.**

Pengguna disarankan untuk melakukan verifikasi terhadap **sumber hukum resmi** dan berkonsultasi dengan profesional hukum apabila membutuhkan analisis atau tindakan hukum yang spesifik.

---

<p align="center">

### ⚖️ AI for Equal Justice

**Mendorong akses informasi hukum yang lebih mudah, transparan, dan inklusif melalui Artificial Intelligence.**

</p>
