import socket
import pyaudio
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import json
import os
import time
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import queue

class AyarlarPenceresi:
    def __init__(self, parent):
        self.pencere = tk.Toplevel(parent)
        self.pencere.title("⚙️ Ayarlar")
        self.pencere.geometry("600x400")
        self.pencere.configure(bg='#2c3e50')
        
        main_frame = tk.Frame(self.pencere, bg='#2c3e50', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        baslik = tk.Label(main_frame, 
                         text="⚙️ Uygulama Ayarları",
                         font=('Arial', 18, 'bold'),
                         bg='#2c3e50', fg='white')
        baslik.pack(pady=(0, 20))
        
        token_frame = tk.LabelFrame(main_frame,
                                    text="  🔑 Ngrok Auth Token  ",
                                    font=('Arial', 11, 'bold'),
                                    bg='#2c3e50', fg='#3498db',
                                    padx=20, pady=15)
        token_frame.pack(fill='x', pady=10)
        
        tk.Label(token_frame,
                text="Token: https://dashboard.ngrok.com/get-started/your-authtoken",
                font=('Arial', 9),
                bg='#2c3e50', fg='#bdc3c7').pack(anchor='w', pady=(0, 10))
        
        token_giris_frame = tk.Frame(token_frame, bg='#2c3e50')
        token_giris_frame.pack(fill='x', pady=5)
        
        self.token_entry = tk.Entry(token_giris_frame,
                                    font=('Courier', 10),
                                    bg='#34495e', fg='white',
                                    insertbackground='white',
                                    show='*',
                                    relief='flat')
        self.token_entry.pack(side='left', fill='x', expand=True, ipady=8)
        
        self.goster_btn = tk.Button(token_giris_frame,
                                    text="👁️",
                                    font=('Arial', 10),
                                    bg='#34495e', fg='white',
                                    command=self.token_goster_gizle,
                                    cursor='hand2',
                                    width=3)
        self.goster_btn.pack(side='right', padx=(5, 0))
        
        current_token = self.token_oku()
        if current_token:
            self.token_entry.insert(0, current_token)
            tk.Label(token_frame,
                    text="✅ Token kaydedilmiş",
                    font=('Arial', 9),
                    bg='#2c3e50', fg='#2ecc71').pack(anchor='w', pady=(5, 0))
        
        self.token_kaydet_btn = tk.Button(token_frame,
                                         text="💾 Token'ı Kaydet",
                                         font=('Arial', 11, 'bold'),
                                         bg='#27ae60', fg='white',
                                         command=self.token_kaydet,
                                         cursor='hand2',
                                         height=2)
        self.token_kaydet_btn.pack(fill='x', pady=(10, 5))
        
        tk.Button(main_frame,
                 text="Kapat",
                 font=('Arial', 11),
                 bg='#95a5a6', fg='white',
                 command=self.pencere.destroy,
                 cursor='hand2',
                 width=15).pack(pady=(20, 0))
        
        self.pencere.transient(parent)
        self.pencere.grab_set()
        self.token_gizli = True
    
    def token_goster_gizle(self):
        if self.token_gizli:
            self.token_entry.config(show='')
            self.goster_btn.config(text='🙈')
            self.token_gizli = False
        else:
            self.token_entry.config(show='*')
            self.goster_btn.config(text='👁️')
            self.token_gizli = True
    
    def token_oku(self):
        config_file = os.path.expanduser("~/.voice_chat_config.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('ngrok_token', '')
        except:
            pass
        return ''
    
    def token_kaydet(self):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showwarning("Uyarı", "Lütfen token giriniz!")
            return
        
        try:
            config_file = os.path.expanduser("~/.voice_chat_config.json")
            with open(config_file, 'w') as f:
                json.dump({'ngrok_token': token}, f)
            
            result = subprocess.run(['ngrok', 'config', 'add-authtoken', token],
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Başarılı", "✅ Token kaydedildi!")
            else:
                messagebox.showerror("Hata", f"Hata:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Hata", f"Hata:\n{e}")


class BaglantiPenceresi:
    def __init__(self, parent, url):
        self.pencere = tk.Toplevel(parent)
        self.pencere.title("🌐 Bağlantı Bilgileri")
        self.pencere.geometry("500x300")
        self.pencere.configure(bg='#2c3e50')
        
        main_frame = tk.Frame(self.pencere, bg='#2c3e50', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        tk.Label(main_frame, 
                text="✅ Sunucu Başlatıldı!",
                font=('Arial', 16, 'bold'),
                bg='#2c3e50', fg='#2ecc71').pack(pady=(0, 20))
        
        tk.Label(main_frame,
                text="Bu URL'yi arkadaşınıza gönderin:",
                font=('Arial', 11),
                bg='#2c3e50', fg='#ecf0f1').pack(pady=(0, 15))
        
        url_frame = tk.Frame(main_frame, bg='#34495e', padx=20, pady=15)
        url_frame.pack(fill='x', pady=5)
        
        tk.Label(url_frame, text="Sunucu URL:",
                font=('Arial', 10, 'bold'),
                bg='#34495e', fg='#bdc3c7').pack(anchor='w')
        
        url_text_frame = tk.Frame(url_frame, bg='#1a1a1a')
        url_text_frame.pack(fill='x', pady=(5, 10))
        
        tk.Label(url_text_frame,
                text=url,
                font=('Courier', 10, 'bold'),
                bg='#1a1a1a', fg='#3498db',
                padx=10, pady=8,
                wraplength=400).pack(side='left', fill='x', expand=True)
        
        tk.Button(url_text_frame,
                 text="📋",
                 font=('Arial', 12),
                 bg='#3498db', fg='white',
                 command=lambda: self.kopyala(url),
                 cursor='hand2',
                 width=3).pack(side='right', padx=5)
        
        tk.Button(main_frame,
                 text="📋 URL'yi Kopyala",
                 font=('Arial', 12, 'bold'),
                 bg='#27ae60', fg='white',
                 command=lambda: self.kopyala(url),
                 cursor='hand2',
                 padx=20, pady=10).pack(pady=20)
        
        tk.Button(main_frame,
                 text="Kapat",
                 font=('Arial', 10),
                 bg='#95a5a6', fg='white',
                 command=self.pencere.destroy,
                 cursor='hand2',
                 width=15).pack()
        
        self.pencere.transient(parent)
        self.pencere.grab_set()
    
    def kopyala(self, text):
        self.pencere.clipboard_clear()
        self.pencere.clipboard_append(text)
        self.pencere.update()
        
        bildirim = tk.Toplevel(self.pencere)
        bildirim.geometry("250x80")
        bildirim.configure(bg='#27ae60')
        bildirim.overrideredirect(True)
        
        x = self.pencere.winfo_x() + (self.pencere.winfo_width() // 2) - 125
        y = self.pencere.winfo_y() + (self.pencere.winfo_height() // 2) - 40
        bildirim.geometry(f"+{x}+{y}")
        
        tk.Label(bildirim,
                text="✅ URL Kopyalandı!",
                font=('Arial', 12, 'bold'),
                bg='#27ae60', fg='white').pack(expand=True)
        
        bildirim.after(1500, bildirim.destroy)


class SesliKonusmaUygulamasi:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        self.audio = pyaudio.PyAudio()
        
        self.ses_queue_giden = queue.Queue()
        self.ses_queue_gelen = queue.Queue()
        
        self.bagli = False
        self.sunucu_calisiyor = False
        self.ngrok_process = None
        self.http_server = None
        self.server_url = None
        
        self.pencere_olustur()
    
    def pencere_olustur(self):
        self.root = tk.Tk()
        self.root.title("🎙️ Sesli Konuşma - HTTP Stream")
        self.root.geometry("600x700")
        self.root.configure(bg='#2c3e50')
        
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        ayarlar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Ayarlar", menu=ayarlar_menu)
        ayarlar_menu.add_command(label="Ngrok Token", command=self.ayarlar_ac)
        ayarlar_menu.add_separator()
        ayarlar_menu.add_command(label="Çıkış", command=self.kapat)
        
        baslik_frame = tk.Frame(self.root, bg='#34495e', pady=15)
        baslik_frame.pack(fill='x')
        
        tk.Label(baslik_frame, 
                text="🎙️ Sesli Konuşma - HTTP Stream", 
                font=('Arial', 18, 'bold'), 
                bg='#34495e', fg='white').pack()
        
        tk.Label(baslik_frame,
                text="HTTP üzerinden ses iletişimi (Ngrok Free ✅)",
                font=('Arial', 9),
                bg='#34495e', fg='#2ecc71').pack()
        
        tk.Button(baslik_frame,
                 text="⚙️",
                 font=('Arial', 14),
                 bg='#34495e', fg='white',
                 command=self.ayarlar_ac,
                 cursor='hand2',
                 relief='flat',
                 width=3).place(relx=0.95, rely=0.5, anchor='e')
        
        sunucu_frame = tk.LabelFrame(self.root, 
                                     text="  🌐 SUNUCU MODU  ",
                                     font=('Arial', 12, 'bold'),
                                     bg='#2c3e50', fg='#3498db',
                                     padx=20, pady=15)
        sunucu_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(sunucu_frame,
                text="HTTP sunucusu başlatın (Ngrok Free ile çalışır!)",
                font=('Arial', 9),
                bg='#2c3e50', fg='#bdc3c7').pack(pady=(0, 10))
        
        self.sunucu_btn = tk.Button(sunucu_frame, 
                                   text="🚀 HTTP Sunucusu Başlat",
                                   command=self.sunucu_baslat,
                                   bg='#9b59b6', fg='white',
                                   font=('Arial', 12, 'bold'),
                                   cursor='hand2',
                                   height=2)
        self.sunucu_btn.pack(fill='x', pady=5)
        
        tk.Label(sunucu_frame,
                text="✅ Ngrok ücretsiz - Port yönlendirme yok!",
                font=('Arial', 8),
                bg='#2c3e50', fg='#2ecc71').pack(pady=(5, 0))
        
        istemci_frame = tk.LabelFrame(self.root, 
                                      text="  🔌 İSTEMCİ MODU  ",
                                      font=('Arial', 12, 'bold'),
                                      bg='#2c3e50', fg='#2ecc71',
                                      padx=20, pady=15)
        istemci_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(istemci_frame,
                text="Arkadaşınızın sunucusuna bağlanın",
                font=('Arial', 9),
                bg='#2c3e50', fg='#bdc3c7').pack(pady=(0, 10))
        
        url_giris_frame = tk.Frame(istemci_frame, bg='#2c3e50')
        url_giris_frame.pack(fill='x', pady=5)
        
        tk.Label(url_giris_frame, text="Sunucu URL:", 
                bg='#2c3e50', fg='white', 
                font=('Arial', 10)).pack(anchor='w')
        
        self.url_entry = tk.Entry(url_giris_frame, 
                                font=('Courier', 10),
                                bg='#34495e', fg='white',
                                insertbackground='white',
                                relief='flat')
        self.url_entry.pack(fill='x', ipady=5)
        self.url_entry.insert(0, "https://example.ngrok-free.app")
        
        self.baglan_btn = tk.Button(istemci_frame, 
                                    text="🔌 Bağlan",
                                    command=self.baglan,
                                    bg='#3498db', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    cursor='hand2',
                                    height=2)
        self.baglan_btn.pack(fill='x', pady=(10, 5))
        
        durum_frame = tk.Frame(self.root, bg='#34495e', padx=20, pady=15)
        durum_frame.pack(pady=10, padx=20, fill='x')
        
        tk.Label(durum_frame, text="DURUM:",
                font=('Arial', 9, 'bold'),
                bg='#34495e', fg='#95a5a6').pack(anchor='w')
        
        self.durum_label = tk.Label(durum_frame, 
                                    text="⚪ Beklemede",
                                    bg='#34495e', fg='#ecf0f1',
                                    font=('Arial', 13, 'bold'))
        self.durum_label.pack(pady=(5, 0))
        
        self.kes_btn = tk.Button(self.root, 
                                text="❌ Bağlantıyı Kes",
                                command=self.baglanti_kes,
                                bg='#e74c3c', fg='white',
                                font=('Arial', 11, 'bold'),
                                cursor='hand2',
                                height=2,
                                state='disabled')
        self.kes_btn.pack(pady=10, padx=20, fill='x')
        
        log_frame = tk.LabelFrame(self.root,
                                 text="  📋 Sistem Logları  ",
                                 font=('Arial', 10, 'bold'),
                                 bg='#2c3e50', fg='#95a5a6',
                                 padx=10, pady=10)
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                   height=8,
                                                   bg='#1a1a1a',
                                                   fg='#00ff00',
                                                   font=('Courier', 9),
                                                   relief='flat',
                                                   wrap='word')
        self.log_text.pack(fill='both', expand=True)
        
        self.log_text.tag_config('SUCCESS', foreground='#2ecc71')
        self.log_text.tag_config('WARNING', foreground='#f39c12')
        self.log_text.tag_config('ERROR', foreground='#e74c3c')
        
        self.log_ekle("✅ Uygulama başlatıldı - HTTP Stream modu", "SUCCESS")
        self.log_ekle("ℹ️  Ngrok FREE versiyonu ile uyumlu!", "SUCCESS")
    
    def ayarlar_ac(self):
        AyarlarPenceresi(self.root)
    
    def log_ekle(self, mesaj, tip="INFO"):
        import datetime
        zaman = datetime.datetime.now().strftime("%H:%M:%S")
        log_mesaj = f"[{zaman}] {mesaj}\n"
        self.log_text.insert(tk.END, log_mesaj, tip)
        self.log_text.see(tk.END)
        print(log_mesaj.strip())
    
    def sunucu_baslat(self):
        """HTTP sunucusunu başlat"""
        self.log_ekle("🚀 HTTP sunucusu başlatılıyor...", "INFO")
        
        app = self
        
        class VoiceHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Logları devre dışı bırak
            
            def do_GET(self):
                """Ses akışı al"""
                if self.path == '/audio':
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    try:
                        while app.bagli:
                            if not app.ses_queue_giden.empty():
                                data = app.ses_queue_giden.get()
                                self.wfile.write(data)
                            else:
                                time.sleep(0.001)
                    except:
                        pass
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'Voice Chat Server Active')
            
            def do_POST(self):
                """Ses akışı gönder"""
                if self.path == '/audio':
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        data = self.rfile.read(content_length)
                        app.ses_queue_gelen.put(data)
                    
                    self.send_response(200)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
        
        # HTTP sunucusunu thread'de başlat
        def run_server():
            self.http_server = HTTPServer(('0.0.0.0', 8765), VoiceHandler)
            self.log_ekle("✅ HTTP sunucusu başlatıldı - http://0.0.0.0:8765", "SUCCESS")
            self.sunucu_calisiyor = True
            self.http_server.serve_forever()
        
        threading.Thread(target=run_server, daemon=True).start()
        
        # Ngrok'u başlat
        time.sleep(1)
        threading.Thread(target=self.ngrok_baslat, daemon=True).start()
        
        self.sunucu_btn.config(state='disabled')
        self.baglan_btn.config(state='disabled')
        self.durum_label.config(text="🟡 Sunucu hazırlanıyor...", fg='#f39c12')
    
    def ngrok_baslat(self):
        """Ngrok tünelini başlat"""
        try:
            self.log_ekle("🌐 Ngrok tüneli başlatılıyor...", "INFO")
            
            self.ngrok_process = subprocess.Popen(
                ['ngrok', 'http', '8765'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            time.sleep(4)
            
            for i in range(10):
                try:
                    response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                    data = response.json()
                    
                    if data.get('tunnels'):
                        for tunnel in data['tunnels']:
                            url = tunnel['public_url']
                            if url.startswith('https://'):
                                self.server_url = url
                                
                                self.log_ekle("=" * 50, "SUCCESS")
                                self.log_ekle(f"🎉 NGROK BAŞARILI!", "SUCCESS")
                                self.log_ekle(f"🔗 URL: {url}", "SUCCESS")
                                self.log_ekle("=" * 50, "SUCCESS")
                                
                                self.root.after(0, lambda: BaglantiPenceresi(self.root, url))
                                self.root.after(0, lambda: self.durum_label.config(text="🟡 Bağlantı bekleniyor...", fg='#f39c12'))
                                return
                except:
                    self.log_ekle(f"⏳ Bekleniyor... ({i+1}/10)", "INFO")
                    time.sleep(2)
            
            self.log_ekle("❌ Ngrok URL alınamadı", "ERROR")
            self.log_ekle("💡 http://localhost:4040 adresini kontrol edin", "WARNING")
            
        except FileNotFoundError:
            self.log_ekle("❌ Ngrok bulunamadı!", "ERROR")
            messagebox.showerror("Hata", "Ngrok yüklü değil!\n\nhttps://ngrok.com/download")
        except Exception as e:
            self.log_ekle(f"❌ Ngrok hatası: {e}", "ERROR")
    
    def baglan(self):
        """Sunucuya bağlan"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Uyarı", "URL giriniz!")
            return
        
        self.server_url = url
        self.bagli = True
        
        self.log_ekle(f"🔄 Bağlanılıyor: {url}", "INFO")
        self.durum_label.config(text="🟢 Bağlı - Konuşabilirsiniz!", fg='#2ecc71')
        
        self.sunucu_btn.config(state='disabled')
        self.baglan_btn.config(state='disabled')
        self.kes_btn.config(state='normal')
        
        # Ses akışlarını başlat
        threading.Thread(target=self.mikrofon_gonder, daemon=True).start()
        threading.Thread(target=self.hoparlor_cal, daemon=True).start()
        threading.Thread(target=self.ses_indir, daemon=True).start()
        threading.Thread(target=self.ses_yukle, daemon=True).start()
        
        self.log_ekle("✅ Bağlantı kuruldu!", "SUCCESS")
    
    def mikrofon_gonder(self):
        """Mikrofonu oku ve kuyruğa ekle"""
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK
            )
            
            self.log_ekle("🎤 Mikrofon aktif", "SUCCESS")
            
            while self.bagli:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                self.ses_queue_giden.put(data)
            
            stream.stop_stream()
            stream.close()
            self.log_ekle("🛑 Mikrofon durduruldu", "INFO")
            
        except Exception as e:
            self.log_ekle(f"❌ Mikrofon hatası: {e}", "ERROR")
    
    def hoparlor_cal(self):
        """Kuyruktan ses al ve çal"""
        try:
            stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.RATE,
                output=True,
                frames_per_buffer=self.CHUNK
            )
            
            self.log_ekle("🔊 Hoparlör aktif", "SUCCESS")
            
            while self.bagli:
                try:
                    data = self.ses_queue_gelen.get(timeout=1)
                    stream.write(data)
                except queue.Empty:
                    continue
            
            stream.stop_stream()
            stream.close()
            self.log_ekle("🛑 Hoparlör durduruldu", "INFO")
            
        except Exception as e:
            self.log_ekle(f"❌ Hoparlör hatası: {e}", "ERROR")
    
    def ses_indir(self):
        """Sunucudan ses indir"""
        while self.bagli:
            try:
                response = requests.get(f"{self.server_url}/audio", stream=True, timeout=5)
                for chunk in response.iter_content(chunk_size=self.CHUNK):
                    if not self.bagli:
                        break
                    if chunk:
                        self.ses_queue_gelen.put(chunk)
            except:
                time.sleep(0.1)
    
    def ses_yukle(self):
        """Sunucuya ses yükle"""
        while self.bagli:
            try:
                if not self.ses_queue_giden.empty():
                    data = self.ses_queue_giden.get()
                    requests.post(f"{self.server_url}/audio", data=data, timeout=1)
            except:
                time.sleep(0.01)
    
    def baglanti_kes(self):
        """Bağlantıyı kes"""
        self.log_ekle("🔴 Bağlantı kesiliyor...", "WARNING")
        
        self.bagli = False
        self.sunucu_calisiyor = False
        
        if self.ngrok_process:
            try:
                self.ngrok_process.terminate()
                self.log_ekle("🔴 Ngrok durduruldu", "WARNING")
            except:
                pass
        
        if self.http_server:
            try:
                self.http_server.shutdown()
            except:
                pass
        
        while not self.ses_queue_giden.empty():
            try:
                self.ses_queue_giden.get_nowait()
            except:
                break
        
        while not self.ses_queue_gelen.empty():
            try:
                self.ses_queue_gelen.get_nowait()
            except:
                break
        
        self.durum_label.config(text="⚪ Beklemede", fg='#ecf0f1')
        self.sunucu_btn.config(state='normal')
        self.baglan_btn.config(state='normal')
        self.kes_btn.config(state='disabled')
        
        self.log_ekle("✅ Bağlantı kesildi", "INFO")
    
    def calistir(self):
        self.root.protocol("WM_DELETE_WINDOW", self.kapat)
        self.root.mainloop()
    
    def kapat(self):
        self.log_ekle("👋 Uygulama kapatılıyor...", "INFO")
        self.baglanti_kes()
        self.audio.terminate()
        self.root.destroy()


if __name__ == "__main__":
    print("=" * 60)
    print("🎙️  SESLİ KONUŞMA - HTTP STREAM (NGROK FREE)")
    print("=" * 60)
    print("\n📦 Gereksinimler:")
    print("   pip install pyaudio requests")
    print("\n🌐 Ngrok Kurulumu:")
    print("   1. https://ngrok.com/download")
    print("   2. Üye olun ve auth token alın")
    print("   3. Uygulamada Ayarlar > Ngrok Token")
    print("\n✅ Ngrok FREE ile çalışır!")
    print("\n🚀 Kullanım:")
    print("   • Sunucu: 'HTTP Sunucusu Başlat'")
    print("   • İstemci: URL girerek 'Bağlan'")
    print("\n💡 Fark:")
    print("   - WebSocket yerine HTTP POST/GET kullanır")
    print("   - Ngrok FREE ile sorunsuz çalışır")
    print("   - Port: 8765")
    print("=" * 60)
    print()
    
    try:
        uygulama = SesliKonusmaUygulamasi()
        uygulama.calistir()
    except KeyboardInterrupt:
        print("\n⚠️  Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
        import traceback
        traceback.print_exc()
