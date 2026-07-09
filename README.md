# meterGPT
Praktek membuat pembacaan meter melalui CCTV - Python - AI OCR via GPT-4o <br>
<img width="1408" height="768" alt="Gemini_Generated_Image_" src="https://github.com/user-attachments/assets/fa7c94f1-0041-485d-92d2-f389defc784a" />
<br>

<img width="1279" height="645" alt="github_meter" src="https://github.com/user-attachments/assets/59d84dd4-91bc-4b4e-bb88-0e5ab0d518c1" />

<br>

<img width="831" height="655" alt="github_meter2" src="https://github.com/user-attachments/assets/4def5220-71b0-4a82-ad83-7b922eef1c23" />

# Konsep Awal

<img width="197" height="274" alt="meter" src="https://github.com/user-attachments/assets/e7e61064-ddfb-44c5-80fc-723465427ca5" />

1. Meter pada panel yang umum di gunakan di gedung-gedung adalah meter generic analog yang kemudian akan di catat secara manual oleh petugas tiap hari pada log
2. Ketika manajemen memerlukan reporting online - realtime, maka hal ini akan susah diwujudkan

# Solusi dengan memanfaatkan chat AI

Ketika gambar diatas diberikan ke chatbot AI seperti gemini dan AI bot lainnya secara mengejutkan semua pembacaan meter dapat diberikan dengan benar <br>

- Prompt : Tolong analisa gambar meter panel yang saya upload  
- Response AI : <br>

Berdasarkan foto panel kontrol yang Anda unggah, berikut adalah analisis dan pembacaan indikator atau alat ukur (meter) analog serta komponen yang terpasang:

### 1. Pembacaan Alat Ukur Analog (Meter)

Di panel ini terdapat 3 buah **Amperemeter** (atas) untuk memantau arus tiap fase (R, S, T) dan 1 buah **Voltmeter** (tengah kiri) untuk memantau tegangan.

* **Amperemeter 1 (Atas Kiri):** Jarum menunjuk sedikit di atas angka 100, diperkirakan berada di kisaran **110 A hingga 120 A**. Skala penuh (maksimum) meteran ini adalah 300 A (dengan batas overload 600 A).
* **Amperemeter 2 (Atas Tengah):** Jarum menunjuk tepat di angka **100 A**.
* **Amperemeter 3 (Atas Kanan):** Jarum menunjuk tepat di angka **100 A**.
* *Analisis Arus:* Beban pada ketiga fase terlihat cukup seimbang (*balanced*), berada di kisaran 100 A hingga 120 A. Keseimbangan beban seperti ini sangat baik untuk menjaga performa motor/kompresor 3 phase dan mencegah panas berlebih pada netral atau motor.


* **Voltmeter (Tengah Kiri):** Jarum menunjuk di angka **400 V**. Skala maksimum meteran adalah 500 V.
* *Analisis Tegangan:* Tegangan 400 V merupakan tegangan *line-to-line* (antar-fase, misalnya R-S, S-T, atau T-R) yang standar dan ideal untuk sistem 3 phase di Indonesia (nominal 380V - 400V). Di bawah voltmeter terdapat *selector switch* (saklar pemilih), yang saat ini posisinya kemungkinan diarahkan untuk membaca salah satu pasangan fase tersebut.



### 2. KWH Meter / Watthour Meter (Tengah Kanan)

Terdapat satu unit KWH meter 3 phase elektromekanis (tipe piringan berputar) merek *Oriental Electric Industry Co., Ltd.* (Lisensi Mitsubishi Electric).

* **Pembacaan Register/Angka:** Angka yang tertera menunjukkan **8 9 5 9**.
* **Catatan Penting Pengukuran:** Pada pelat nama KWH meter jenis ini, biasanya terdapat instruksi **"MULTIPLY BY CT RATIO"** (Kalikan dengan Rasio CT). Karena sistem ini menggunakan arus besar (~100A), KWH meter tidak dilewati arus secara langsung, melainkan menggunakan *Current Transformer* (CT).
* Untuk mendapatkan nilai konsumsi energi (kWh) yang sebenarnya untuk pelaporan atau *logging*, Anda harus **mengalikan angka 8959 tersebut dengan rasio CT** yang terpasang di dalam panel (misalnya jika CT yang digunakan adalah 150/5A, maka rasionya adalah 30 kali).

### 3. Lampu Indikator & Komponen Lain

* **Lampu Tanda (Pilot Lamp):** Di bagian paling atas terdapat lampu indikator fase. Terlihat dua lampu menyala (merah dan kuning/oranye) serta satu lampu hijau di kanan atas. Ini menandakan bahwa suplai daya 3 phase masuk ke panel dalam kondisi aktif.
* **Lembar SOP (Bawah):** Terdapat dokumen cetak bertuliskan **"PENGOPERASIAN CHILLER SECARA MANUAL SELAMA KOMPRESOR JALAN 1"**. Ini mengonfirmasi bahwa panel ini berfungsi untuk mengontrol atau memonitor sistem pendingin (*chiller*) industri, di mana kestabilan arus (~100A) dan tegangan (400V) yang kita baca di atas sangat krusial untuk menjaga kompresor *chiller* tetap bekerja dengan aman.

Secara keseluruhan, jika dilihat dari meternya, sistem saat ini beroperasi dengan normal dan stabil pada tegangan 400V dengan beban arus tiap fase yang seimbang di kisaran 100-120 Ampere.



# Panduan Praktek 

1. CCTV yang saya gunakan merupakan cctv umum IPcam dengan akses RTSP
2. Dapat juga menggunakan kamera HP dengan tambahan apk yg bisa merubahnya menjadi stream RTSP
3. Panel di praktek berupa pilot lamp dengan display 7 segmen ber-sensor tegangan dan arus (CT / current transformer)
4. Python akan melakukan pengambilan gambar stream CCTV (1 frame saja) lalu memotongnya di POI pilot lamp 7 segmen (agar lebih kecil) lalu diupload ke chatAI nya github dan diberikan prompt yang tepat
5. Response akan diberikan AI lalu hasil pembacaan dikirimkan melalui MQTT untuk selanjutnya secara realtime dapat dibaca oleh yg membutuhkan baik database, website dashboard, aplikasi dsb.
6. Contoh python dan HTML nya sudah tersedia
