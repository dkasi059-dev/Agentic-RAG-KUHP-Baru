# ⚖️ Agentic RAG KUHP Baru

### AI-Powered Legal Assistant untuk Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana

<p align="center">
  <img src="assets/logo.png" alt="Agentic RAG KUHP Baru Logo" width="373">
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

Proyek ini mengimplementasikan pendekatan **Agentic Retrieval-Augmented Generation (Agentic RAG)** yang mengombinasikan kemampuan **Large Language Model (LLM)**, retrieval dokumen hukum, workflow agen berbasis **LangGraph**, serta berbagai sumber informasi pendukung. Berbeda dari sistem pencarian berbasis kata kunci sederhana, agen dirancang untuk memahami konteks pertanyaan, menentukan informasi yang dibutuhkan, melakukan retrieval terhadap sumber yang relevan, melakukan pencarian sumber yang dibutuhkan di internet (sumber eksternal), mengevaluasi kecukupan informasi, dan menghasilkan jawaban berdasarkan konteks yang diperoleh. Selain itu, sistem ini juga bisa menolak pertanyaan yang tidak berhubungan dengan KUHP Baru waluapun mengandung kata kunci yang menyerupai pertanyaan tentang KUHP Baru. Sistem juga dilengkapi dengan **conversation memory**, sehingga konteks pertanyaan sebelumnya dapat dipertahankan selama sesi percakapan. Hal tersebut memungkinkan pengguna mengajukan pertanyaan lanjutan tanpa harus mengulangi seluruh konteks pembicaraan.

> **AI for Equal Justice** — teknologi AI dimanfaatkan sebagai sarana pendukung untuk memperluas akses terhadap informasi seputar KUHP Baru yang akurat, transparan, dan mudah dipahami.

---

## 🎯 Latar Belakang

Perkembangan kecerdasan buatan telah membuka peluang baru dalam penyediaan layanan informasi di berbagai bidang, termasuk bidang hukum. Di Indonesia, kebutuhan terhadap akses informasi hukum semakin relevan setelah diberlakukannya **Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana (KUHP Baru)**. KUHP Baru memiliki struktur dan substansi yang kompleks serta memuat **624 pasal**. Bagi masyarakat yang tidak memiliki latar belakang hukum, memahami keseluruhan ketentuan tersebut dapat menjadi tantangan. Permasalahan semakin kompleks ketika pencarian informasi hukum dilakukan menggunakan sistem berbasis keyword search. Pencarian berbasis kata kunci dapat menemukan dokumen yang mengandung istilah tertentu, tetapi belum tentu memahami:
* konteks pertanyaan;
* maksud pengguna;
* hubungan antarketentuan;
* konsep hukum yang sedang ditanyakan;
* informasi apa yang sebenarnya dibutuhkan;
* serta bagaimana menjelaskan ketentuan hukum dalam bahasa yang mudah dipahami.

Di sisi lain, penggunaan LLM tanpa sumber eksternal atau mekanisme retrieval memiliki risiko **hallucination**, yaitu menghasilkan informasi yang terdengar meyakinkan tetapi tidak memiliki dasar yang benar. Oleh karena itu, proyek ini mengadopsi pendekatan **Agentic RAG** untuk menggabungkan kemampuan reasoning LLM dengan retrieval terhadap sumber hukum.

---

# ❗ Problem Statement

### Permasalahan Utama

Terdapat beberapa permasalahan yang ingin diselesaikan melalui proyek ini:

1. **Kompleksitas KUHP Baru**
   <br>KUHP Baru terdiri dari 624 pasal sehingga membutuhkan waktu dan ketelitian untuk dipelajari secara menyeluruh.
3. **Kesulitan masyarakat memahami bahasa hukum**
   Istilah dan struktur bahasa hukum sering kali sulit dipahami oleh masyarakat yang tidak memiliki latar belakang hukum.
4. **Keterbatasan keyword search**
   Sistem pencarian konvensional cenderung berorientasi pada kecocokan kata, bukan pemahaman terhadap konteks pertanyaan.
5. **Keterbatasan LLM tanpa retrieval**
   LLM dapat menghasilkan jawaban yang tidak memiliki dasar hukum yang memadai apabila tidak diberikan sumber informasi yang relevan.
6. **Kebutuhan terhadap informasi hukum yang dapat ditelusuri**
   Jawaban hukum idealnya dapat dikaitkan kembali dengan sumber hukum yang menjadi dasar informasi tersebut.

### Solusi yang Ditawarkan

Proyek ini menggunakan pendekatan **Agentic Retrieval-Augmented Generation** sehingga sistem dapat:

<p align="left">
  <img src="assets/Graph 1.png" alt="Agentic RAG KUHP Baru Logo" width="373">
</p>

Dengan demikian, sistem tidak hanya berfungsi sebagai chatbot, tetapi sebagai **agen yang dapat menentukan langkah yang diperlukan untuk menghasilkan jawaban**.

---

# 👥 Target Pengguna
Aplikasi dirancang untuk berbagai kelompok pengguna setidak-tidaknya dapat digunakan oleh pihak-pihak di bawah ini.

**1. Masyarakat Umum**

Membantu memperoleh pemahaman awal mengenai ketentuan KUHP Baru tanpa harus memahami terminologi hukum secara mendalam.

**2. Mahasiswa dan Pelajar**

Dapat digunakan sebagai media pembelajaran interaktif untuk mengeksplorasi konsep, pasal, serta hubungan antarketentuan dalam KUHP Baru.

**3. Akademisi dan Peneliti**

Mendukung proses eksplorasi dan penelusuran informasi hukum dalam kegiatan akademik dan penelitian.

**4. Praktisi Hukum**

Dapat digunakan sebagai alat bantu pencarian awal terhadap referensi hukum.

**5. Instansi Pemerintah dan Pelayanan Publik**

Berpotensi digunakan sebagai pendukung penyediaan informasi hukum kepada masyarakat.

---

# ✨ Fitur Utama

🤖 **Agentic RAG**
Menggunakan workflow agen untuk menentukan langkah retrieval dan reasoning secara adaptif.
📚 **KUHP Baru sebagai Knowledge Base Utama**
Dokumen **Kitab Undang-Undang Hukum Pidana (KUHP) Baru** digunakan sebagai sumber pengetahuan utama sistem.
🧠 **LLM Reasoning**
LLM digunakan untuk memahami pertanyaan, mengintegrasikan informasi, serta menyusun jawaban berdasarkan konteks.
🔎 **Multi-Source Retrieval**
Sistem dapat memanfaatkan sumber informasi internal maupun eksternal sesuai kebutuhan.
💬 **Conversation Memory**
Konteks percakapan dipertahankan selama sesi sehingga pengguna dapat mengajukan pertanyaan lanjutan secara natural.
🔄 **Iterative Retrieval**
Apabila informasi yang diperoleh belum memadai, workflow dapat kembali melakukan retrieval untuk memperoleh informasi tambahan.
📖 **Source-Grounded Answer**
Jawaban diarahkan agar tetap berlandaskan sumber informasi yang digunakan dalam proses retrieval.
📊 **Observability**
Proses workflow agen dapat dipantau selama pengembangan dan evaluasi menggunakan LangSmith.

---

# 🏗️ Arsitektur Sistem

Secara konseptual, arsitektur sistem terdiri atas beberapa lapisan sebagai berikut ini.

<p align="left">
  <img src="assets/Graph 2.png" alt="Agentic RAG KUHP Baru Logo" width="373">
</p>

Arsitektur tersebut menggambarkan proses sistem dalam menerima, mengolah, dan menghasilkan jawaban atas pertanyaan pengguna. Secara ringkas penjelasan alur di atas adalah sebagai berikut ini:
1. Proses dimulai ketika pengguna berinteraksi melalui Antarmuka Streamlit sebagai media untuk memasukkan pertanyaan.
2. Selanjutnya, sistem melakukan analisis pertanyaan guna memahami maksud dan kebutuhan informasi.
3. Setelah itu, sistem menentukan apakah pertanyaan tersebut relevan. Jika tidak relevan, proses dihentikan dan sistem memberikan keterangan bahwa pertanyaan tidak berkaitan dengan KUHP Baru sehingga sistem tidak dapat memberikan jawaban lebih lanjut.
4. Jika relevan, proses dilanjutkan ke tahap Pemilihan Sumber untuk menentukan sumber informasi yang sesuai.
5. Kemudian, sistem melakukan Pengambilan Multi-sumber dengan mengumpulkan informasi dari berbagai sumber yang tersedia.
6. Informasi tersebut selanjutnya dievaluasi untuk menilai tingkat kecukupannya, baik cukup, sebagian, maupun belum cukup.
7. Berdasarkan hasil evaluasi, sistem menyusun jawaban akhir yang paling sesuai dengan pertanyaan dan informasi yang diperoleh.
8. Tahap terakhir adalah pemberian respons kepada pengguna.

Dengan demikian, alur ini menunjukkan proses yang sistematis, mulai dari pemahaman pertanyaan, validasi relevansi, pencarian informasi, evaluasi sumber, hingga penyusunan jawaban akhir yang diharapkan akurat dan relevan. Pendekatan ini membantu sistem menjaga ketepatan informasi, mengurangi kesalahan, dan memastikan respons akhir tetap relevan dengan kebutuhan pengguna secara lebih konsisten.

---

# 📚 Knowledge Base

Sumber pengetahuan utama aplikasi adalah:

<p align="left">
  <img src="assets/Ilustrasi.png" alt="Agentic RAG KUHP Baru Logo" width="373">
</p>

Dokumen tersebut berisi teks **Undang-Undang Nomor 1 Tahun 2023 tentang Kitab Undang-Undang Hukum Pidana** yang digunakan sebagai basis informasi utama dalam proses retrieval. Prioritas terhadap dokumen hukum utama dimaksudkan agar jawaban yang berkaitan langsung dengan substansi KUHP tetap memiliki landasan hukum yang jelas. Sumber eksternal hanya digunakan sebagai informasi pendukung ketika dibutuhkan, bukan sebagai pengganti sumber hukum utama.

---

# 🔎 Retrieval & External Tools

Sistem dapat menggunakan beberapa sumber informasi pendukung.

**KUHP Baru**
Merupakan **knowledge source intenal utama** untuk pertanyaan yang berkaitan dengan substansi KUHP Baru.
**Wikipedia**
Digunakan untuk membantu memperoleh informasi konseptual mengenai istilah atau konsep tertentu.
**arXiv**
Digunakan untuk memperoleh referensi akademik yang relevan.
**Tavily Search**
Digunakan untuk memperoleh informasi eksternal dan informasi terbaru yang membutuhkan pencarian web.

---

# 💬 Conversation Memory

Aplikasi mendukung percakapan multi-turn, yakni bentuk dialog yang terdiri dari dua atau lebih pertukaran pesan beruntun di mana arti dan respons yang tepat bergantung pada apa yang dikatakan pada tahap sebelumnya.

Contohnya:

```text
User:
Apa bunyi pasal 3 KUHP Baru?

Agent:
[Jawaban mengenai pasal 3 yang terdiri dari 7 ayat.]

User:
Jelaskan ayat 7 di atas?

Agent:
[Jawaban menggunakan konteks percakapan sebelumnya. Agen mengetahui bahwa yang dimaksud ayat 7 di pasal 3 bukan pasal lain.]

User:
Jelaskan ayat sebelumnya?

Agent:
[Jawaban menggunakan konteks percakapan sebelumnya. Agen mengetahui bahwa yang dimaksud ayat sebelumnya adalah ayat 6 pasal 3 karena konteks percakapan sebelumnya pasal 3 ayat 7.]
```

Dengan mekanisme tersebut, pengguna tidak selalu perlu mengulang konteks pada setiap pertanyaan. Conversation memory sangat berguna ketika pengguna melakukan eksplorasi hukum secara bertahap.

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

# ⚠️ Limitations

Proyek ini memiliki beberapa keterbatasan.
**1. Potensi Halusinasi**
Meskipun Agentic RAG dirancang untuk mengurangi halusinasi melalui retrieval dan evaluasi, sistem berbasis LLM tetap memiliki kemungkinan menghasilkan informasi yang tidak sempurna, walaupun kemungkinan itu sangat kecil.
**2. Ketergantungan terhadap Sumber**
Kualitas jawaban sangat dipengaruhi oleh kualitas dan kelengkapan sumber yang tersedia. Apabila ada perubahan-perubahan pasal dalam KUHP Baru maka sistem tidak serta merta akan mengikuti perubahan terbaru tersebut, melainkan harus dilakukan penyesuaian terhadap sumber dokumen utama.
**3. Keterbatasan Model**
Sistem ini masih menggunakan model gratis dengan kapasitas tertentu dapat memiliki keterbatasan context window, rate limit, reasoning capability, jumlah pemanggilan tools, dan jumlah pencarian sumber-sumber eksternal.
**4. Belum terdapat halaman pembuatan akun pengguna**
Walaupun di sisi lain memudahkan pengguna saat menggunakan sistem ini karena tidak perlu membuat dan masuk ke akun, ketiadaan halaman akun pengguna menyebabkan riwayat pesan hanya bertahan dalam satu sesi percakapan. Artinya, jika pengguna meninggalkan halaman ini atau koneksi internet terputus maka seluruh riwayat percakapan akan hilang.

---

# 🔒 Responsible AI

Karena aplikasi berada dalam domain hukum, penggunaan AI perlu dilakukan secara bertanggung jawab. Prinsip yang digunakan dalam proyek ini meliputi:
* mengutamakan sumber hukum sebagai landasan;
* membedakan informasi hukum dari interpretasi AI;
* tidak memosisikan AI sebagai pengganti profesional hukum;
* mendorong verifikasi terhadap sumber resmi;
* menjaga kerahasiaan API credentials;
* serta menyadari keterbatasan model generatif.
Tujuan utama sistem adalah **mempermudah akses terhadap informasi hukum**, bukan memberikan keputusan hukum yang mengikat.

---

# 🌱 Impact

Teknologi AI memiliki potensi untuk membantu mengurangi hambatan akses terhadap informasi hukum. Melalui aplikasi ini, pengguna dapat memperoleh sarana untuk:
* memahami konsep hukum;
* mencari ketentuan dalam KUHP Baru;
* mengeksplorasi pertanyaan hukum layaknya sedang bercakap-cakap dengan rekannya;
* menemukan informasi yang relevan dengan lebih cepat;
* serta memahami informasi hukum dengan bahasa yang lebih mudah dicerna.
Dampak yang diharapkan tidak hanya bersifat teknis, tetapi juga sosial melalui peningkatan **literasi hukum** dan akses terhadap informasi.

---

# 🔮 Future Development

Pengembangan selanjutnya dapat diarahkan pada beberapa aspek.
🗄️ **Vector Database**
Mengintegrasikan vector database untuk memungkinkan semantic retrieval yang lebih efisien ketika jumlah dokumen semakin besar.
🤖 **Model yang Lebih Cerdas**
Mengganti model gratis yang memiliki beberapa keterbatasan dengan model berbayar yang lebih cerdas dan memiliki keterbatasan yang relatif lebih sedikit untuk meningkatkan kemampuan reasoning, terutama untuk pertanyaan hukum yang membutuhkan analisis multi-langkah, dan memperbanyak jumlah pencarian sumber eksternal.
💬 **Halaman Pengguna**
Menambahkan halaman pembuatan akun pengguna agar tiap pengguna yang menggunakan sistem ini memiliki halaman pribadi yang dapat menyimpan seluruh riwayat percakapan sebelumnya agar dapat membaca atau meneruskan percakapan kapan pun pengguna menginginkannya. 
📚 **Multi-Regulation Knowledge Base**
Memperluas knowledge base dari KUHP menjadi berbagai regulasi lain, seperti KUHAP, KUHPerdata, peraturan pemerintah, peraturan sektoral, serta regulasi nasional lainnya.
📑 **Hasil yang Lebih Terstruktur**
Mengembangkan mekanisme sitasi pasal secara lebih terstruktur sehingga pengguna dapat mengetahui dasar hukum dari setiap bagian jawaban. Selain itu, juga perlu membangun representasi hubungan dalam bentuk visual/grafik menggenai unsur tindak pidana, sanksi, pengecualian, dan pasal terkait
sehingga hubungan antar ketentuan dapat dieksplorasi secara visual.

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

**Agentic RAG KUHP Baru merupakan sistem berbasis kecerdasan buatan untuk membantu akses dan pemahaman awal terhadap informasi hukum. Sistem ini bukan merupakan pengganti konsultasi hukum profesional dan tidak memberikan nasihat hukum yang mengikat.** Pengguna disarankan untuk melakukan verifikasi terhadap **sumber hukum resmi** dan berkonsultasi dengan profesional hukum apabila membutuhkan analisis atau tindakan hukum yang spesifik.

---

<p align="center">

### ⚖️ EquiLawForJustice: AI for Equal Justice

**Mendorong akses informasi hukum yang lebih mudah, transparan, dan inklusif melalui Artificial Intelligence.**

</p>
