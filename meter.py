import cv2
import requests
import base64
import json
import time
import re
import paho.mqtt.client as mqtt

# =====================================================================
# 1. KONFIGURASI UTAMA
# =====================================================================
GITHUB_TOKEN = "xxxxxxxxxxxxxxxxxxxxxxx" # minta ke pak nyoman kalau mau menjalankan
URL_API = "https://models.inference.ai.azure.com/chat/completions"
NAMA_MODEL = "gpt-4o"
#NAMA_MODEL ="Llama-3.2-11B-Vision-Instruct"
RTSP_URL = "rtsp://admin:1234567890@192.168.100.153:8554/Streaming/Channels/101"

# Konfigurasi Broker MQTT (Gunakan EMQX yang stabil sebagai alternatif)
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC = "/aisi555/meter"

INTERVAL_DETEKSI = 30.0  # Diubah menjadi 30 detik sesuai request

# =====================================================================
# 2. INISIALISASI MQTT
# =====================================================================
print("[INFO] Menghubungkan ke Broker MQTT...")
mqtt_client = mqtt.Client()
try:
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    print("[SUCCESS] Terhubung ke Broker MQTT!")
except Exception as e:
    print(f"[ERROR] Gagal ke MQTT: {e}")
    exit()

# =====================================================================
# 3. FUNGSI AMBIL SNAPSHOT (BUKA -> AMBIL -> TUTUP)
# =====================================================================
def ambil_frame_cctv():
    print("\n[CCTV] Membuka akses kamera (Connect RTSP)...")
    cap = cv2.VideoCapture(RTSP_URL)
    
    if not cap.isOpened():
        print("[ERROR] Gagal membuka stream CCTV. Kamera mungkin sibuk.")
        return None

    # Biarkan kamera stabil sejenak (buang 5 frame awal agar tidak blur/gelap)
    for _ in range(5):
        cap.read()
        
    ret, frame = cap.read()
    
    # LANGKAH KRUSIAL: Putus hubungan dengan kamera segera setelah dapat gambar
    cap.release()
    print("[CCTV] Frame berhasil diambil. Akses kamera DIPUTUS (Disconnect).")
    
    if ret:
        return frame
    return None

# =====================================================================
# 4. FUNGSI PROSES AI & KIRIM DATA
# =====================================================================
def proses_dan_kirim_data(frame_asli):
    # Hitung koordinat CROP otomatis di tengah gambar HD
    height, width = frame_asli.shape[:2]
    box_w, box_h = 250, 250  
    x1, y1 = int((width - box_w) / 2), int((height - box_h) / 2)
    cropped_area = frame_asli[y1:y1+box_h, x1:x1+box_w]
    
    # === BARIS BARU: Simpan gambar crop secara lokal untuk kalibrasi ===
    # Gambar ini akan terus diperbarui (di-overwrite) setiap 30 detik
    cv2.imwrite("live_crop.jpg", cropped_area)
    print("[INFO] Gambar 'live_crop.jpg' berhasil diperbarui untuk kalibrasi.")
    # ==================================================================
    
    # Konversi hasil crop ke Base64 untuk dikirim ke GPT
    _, buffer = cv2.imencode('.jpg', cropped_area)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    

    
    perintah_prompt = """
    Anda adalah OCR industri untuk display LED 7-Segment merah. Baca angka mentah pada gambar.
    Format output WAJIB hanya teks ini tanpa basa-basi pengantar:
    Tegangan: [angka ratusan bulat] V
    Arus: [angka desimal] A
    """
    
    payload = {
        "model": NAMA_MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": perintah_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
            ]
        }],
        "temperature": 0.0
    }
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}", "Content-Type": "application/json"}
    
    try:
        response = requests.post(URL_API, headers=headers, data=json.dumps(payload), timeout=15)
        res_json = response.json()
        text_output = res_json['choices'][0]['message']['content'].strip()
        
        print(f"--- BALASAN {NAMA_MODEL} ---")
        print(text_output)
        print("----------------------------")
        
        # Ekstraksi Regex
        match_v = re.search(r"Tegangan:\s*([\d.]+)", text_output)
        match_a = re.search(r"Arus:\s*([\d.]+)", text_output)
        
        if match_v and match_a:
            v_val = float(match_v.group(1))
            a_val = float(match_a.group(1))
            w_val = round(v_val * a_val, 2)
            
            data_payload = {
                "tegangan": v_val,
                "arus": a_val,
                "watt": w_val,
                "timestamp": int(time.time())
            }
            
            mqtt_client.publish(MQTT_TOPIC, json.dumps(data_payload))
            print(f"[MQTT] Terkirim -> {data_payload}")
            
    except Exception as e:
        print(f"[ERROR] Kegagalan sistem AI/API: {e}")

# =====================================================================
# 5. LOOP UTAMA (BACKGROUND AUTOMATION)
# =====================================================================
print(f"\n[SISTEM] Otomatisasi berjalan tiap {int(INTERVAL_DETEKSI)} detik.")
print("[SISTEM] Tekan Ctrl+C di CMD jika ingin menghentikan program.\n")

try:
    while True:
        waktu_mulai_siklus = time.time()
        
        # 1. Ambil gambar (Kamera On lalu langsung Off)
        frame = ambil_frame_cctv()
        
        if frame is not None:
            # 2. Proses ke GPT dan kirim ke MQTT jika gambar berhasil didapat
            proses_dan_kirim_data(frame)
        else:
            print("[WARNING] Siklus ini dilewati karena gagal mengambil gambar dari CCTV.")
            
        # 3. Hitung sisa waktu untuk tidur (Sleep) agar pas 30 detik
        waktu_proses = time.time() - waktu_mulai_siklus
        waktu_tidur = INTERVAL_DETEKSI - waktu_proses
        
        if waktu_tidur > 0:
            print(f"[SLEEP] Sistem istirahat selama {waktu_tidur:.2f} detik...")
            time.sleep(waktu_tidur)
            
except KeyboardInterrupt:
    print("\n[INFO] Menghentikan program secara aman...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("[INFO] Program ditutup.")
