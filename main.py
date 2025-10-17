import socket
import pyaudio
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import subprocess
import requests
import json
import time

class SesliKonusmaUygulamasi:
    def __init__(self):
        # Ses ayarları
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        # PyAudio başlat
        self.audio = pyaudio.PyAudio()
        
        # Socket bağlantıları
        self.server_socket = None
        self.client_socket = None
        self.baglanti = None
        
        # Ngrok değişkenleri
        self.ngrok_process = None
        self.ngrok_url = None
        
        # Durum değişkenleri
        self.bagli = False
        self.dinleme_aktif = False
        
        # GUI oluştur
        self.pencere_olustur()
    
    def pencere_olustur(self):
        """Arayüz penceresi oluştur"""
        self.root = tk.Tk()
        self.root.title("🎙️ Sesli Konuşma Uygulaması (Ngrok)")
        self.root.geometry("550x750")
        self.root.configure(bg='#2c3e50')
        
        # Başlık
        baslik = tk.Label(self.root, text="🎙️ Sesli Konuşma", 
                         font=('Arial', 20, 'bold'), 
                         bg='#2c3e50', fg='white')
        baslik.pack(pady=20)
        
        # Bağlantı bilgileri frame
        baglanti_frame = tk.Frame(self.root, bg='#34495e', padx=20, pady=20)
        baglanti_frame.pack(pady=10, padx=20, fill='x')
        
        # IP adresi
        tk.Label(baglanti_frame, text="IP Adresi:", 
                bg='#34495e', fg='white', font=('Arial', 11)).grid(row=0, column=0, sticky='w', pady=5)
        self.ip_entry = tk.Entry(baglanti_frame, width=30, font=('Arial', 11))
        self.ip_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Port
        tk.Label(baglanti_frame, text="Port:", 
                bg='#34495e', fg='white', font=('Arial', 11)).grid(row=1, column=0, sticky='w', pady=5)
        self.port_entry = tk.Entry(baglanti_frame, width=30, font=('Arial', 11))
        self.port_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Butonlar frame
        buton_frame = tk.Frame(self.root, bg='#2c3e50')
        buton_frame.pack(pady=20)
        
        # Sunucu olarak başlat butonu (Ngrok ile)
        self.sunucu_btn = tk.Button(buton_frame, text="📡 Sunucu Başlat (Ngrok)",
                                     command=self.ngrok_sunucu_baslat,
                                     bg='#27ae60', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     width=22, height=2,
                                     cursor='hand2')
        self.sunucu_btn.grid(row=0, column=0, padx=10, pady=5)
        
        # Bağlan butonu
        self.baglan_btn = tk.Button(buton_frame, text="🔌 Bağlan",
                                     command=self.baglan,
                                     bg='#3498db', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     width=22, height=2,
                                     cursor='hand2')
        self.baglan_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Bağlantıyı kes butonu
        self.kes_btn = tk.Button(buton_frame, text="❌ Bağlantıyı Kes",
                                  command=self.baglanti_kes,
                                  bg='#e74c3c', fg='white',
                                  font=('Arial', 12, 'bold'),
                                  width=46, height=2,
                                  cursor='hand2',
                                  state='disabled')
        self.kes_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Ngrok Bağlantı Bilgileri Frame
        self.ngrok_bilgi_frame = tk.Frame(self.root, bg='#9b59b6', padx=15, pady=15)
        self.ngrok_bilgi_frame.pack(pady=10, padx=20, fill='x')
        self.ngrok_bilgi_frame.pack_forget()  # Başlangıçta gizli
        
        tk.Label(self.ngrok_bilgi_frame, text="🌐 NGROK BAĞLANTI BİLGİLERİ",
                bg='#9b59b6', fg='white',
                font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # IP ve Port bilgisi frame
        bilgi_detay_frame = tk.Frame(self.ngrok_bilgi_frame, bg='#8e44ad', padx=10, pady=8)
        bilgi_detay_frame.pack(fill='x', pady=5)
        
        self.ngrok_ip_label = tk.Label(bilgi_detay_frame, text="IP: -",
                                       bg='#8e44ad', fg='white',
                                       font=('Courier', 11, 'bold'))
        self.ngrok_ip_label.pack(anchor='w')
        
        self.ngrok_port_label = tk.Label(bilgi_detay_frame, text="Port: -",
                                         bg='#8e44ad', fg='white',
                                         font=('Courier', 11, 'bold'))
        self.ngrok_port_label.pack(anchor='w')
        
        # Kopyala butonları
        kopyala_frame = tk.Frame(self.ngrok_bilgi_frame, bg='#9b59b6')
        kopyala_frame.pack(pady=10)
        
        self.ip_kopyala_btn = tk.Button(kopyala_frame, text="📋 IP Kopyala",
                                        command=lambda: self.panoya_kopyala(self.ngrok_ip_label.cget("text").replace("IP: ", "")),
                                        bg='#e67e22', fg='white',
                                        font=('Arial', 10, 'bold'),
                                        cursor='hand2')
        self.ip_kopyala_btn.pack(side='left', padx=5)
        
        self.port_kopyala_btn = tk.Button(kopyala_frame, text="📋 Port Kopyala",
                                          command=lambda: self.panoya_kopyala(self.ngrok_port_label.cget("text").replace("Port: ", "")),
                                          bg='#e67e22', fg='white',
                                          font=('Arial', 10, 'bold'),
                                          cursor='hand2')
        self.port_kopyala_btn.pack(side='left', padx=5)
        
        self.tumunu_kopyala_btn = tk.Button(kopyala_frame, text="📋 Tümünü Kopyala",
                                           command=self.tumunu_kopyala,
                                           bg='#d35400', fg='white',
                                           font=('Arial', 10, 'bold'),
                                           cursor='hand2')
        self.tumunu_kopyala_btn.pack(side='left', padx=5)
        
        # Durum göstergesi
        self.durum_frame = tk.Frame(self.root, bg='#34495e', padx=20, pady=15)
        self.durum_frame.pack(pady=10, padx=20, fill='x')
        
        self.durum_label = tk.Label(self.durum_frame, 
                                    text="⚪ Bağlantı Bekleniyor",
                                    bg='#34495e', fg='#ecf0f1',
                                    font=('Arial', 12, 'bold'))
        self.durum_label.pack()
        
        # Log alanı
        log_frame = tk.Frame(self.root, bg='#2c3e50')
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        tk.Label(log_frame, text="📋 Durum Logları:", 
                bg='#2c3e50', fg='white', 
                font=('Arial', 11, 'bold')).pack(anchor='w')
        
        self.log_text = scrolledtext.ScrolledText(log_frame, 
                                                   height=8,
                                                   bg='#1a1a1a',
                                                   fg='#00ff00',
                                                   font=('Courier', 9))
        self.log_text.pack(fill='both', expand=True)
        
        # Ngrok bilgi kutusu
        ngrok_info_frame = tk.Frame(self.root, bg='#16a085', padx=10, pady=8)
        ngrok_info_frame.pack(pady=5, padx=20, fill='x')
        
        ngrok_text = "💡 Sunucu Başlat butonuna basın, ngrok auth token girin.\nİnternet üzerinden herkes bağlanabilir!"
        tk.Label(ngrok_info_frame, text=ngrok_text,
                bg='#16a085', fg='white',
                font=('Arial', 9, 'bold'), justify='left').pack()
        
        self.log_ekle("✅ Uygulama başlatıldı")
        self.log_ekle("ℹ️  Sunucu başlatmak için Ngrok auth token gerekli")
        self.log_ekle("🌐 Token: https://dashboard.ngrok.com/get-started/your-authtoken")
    
    def log_ekle(self, mesaj):
        """Log mesajı ekle"""
        import datetime
        zaman = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{zaman}] {mesaj}\n")
        self.log_text.see(tk.END)
    
    def ngrok_sunucu_baslat(self):
        """Ngrok ile sunucu başlat"""
        # Auth token iste
        auth_token = simpledialog.askstring(
            "Ngrok Auth Token",
            "Ngrok auth token'ınızı girin:\n(https://dashboard.ngrok.com/get-started/your-authtoken)",
            parent=self.root
        )
        
        if not auth_token:
            self.log_ekle("❌ Auth token girilmedi, işlem iptal edildi")
            return
        
        try:
            # Yerel sunucuyu başlat
            self.log_ekle("🔧 Yerel sunucu başlatılıyor...")
            local_port = 5000
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', local_port))
            self.server_socket.listen(1)
            
            self.log_ekle(f"✅ Yerel sunucu başlatıldı - Port: {local_port}")
            
            # Ngrok'u başlat
            self.log_ekle("🚀 Ngrok başlatılıyor...")
            ngrok_komut = f'ngrok tcp {local_port} --authtoken {auth_token}'
            
            self.ngrok_process = subprocess.Popen(
                ngrok_komut,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Ngrok API'den bilgileri al
            time.sleep(3)  # Ngrok'un başlaması için bekle
            
            threading.Thread(target=self.ngrok_bilgilerini_al, daemon=True).start()
            
            # Bağlantı beklemeye başla
            self.log_ekle("⏳ Bağlantı bekleniyor...")
            self.durum_label.config(text="🟡 Ngrok Hazırlanıyor...", fg='#f39c12')
            
            self.sunucu_btn.config(state='disabled')
            self.baglan_btn.config(state='disabled')
            
            # Arka planda bağlantı bekle
            threading.Thread(target=self.baglanti_kabul_et, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu başlatılamadı: {e}")
            self.log_ekle(f"❌ Hata: {e}")
            self.ngrok_durdur()
    
    def ngrok_bilgilerini_al(self):
        """Ngrok API'den bağlantı bilgilerini al"""
        max_deneme = 10
        for i in range(max_deneme):
            try:
                response = requests.get('http://localhost:4040/api/tunnels')
                data = response.json()
                
                if 'tunnels' in data and len(data['tunnels']) > 0:
                    tunnel = data['tunnels'][0]
                    public_url = tunnel['public_url']
                    
                    # tcp://x.tcp.ngrok.io:12345 formatından IP ve port çıkar
                    if 'tcp://' in public_url:
                        url_parts = public_url.replace('tcp://', '').split(':')
                        ngrok_ip = url_parts[0]
                        ngrok_port = url_parts[1]
                        
                        self.log_ekle(f"🌐 Ngrok URL: {public_url}")
                        self.log_ekle(f"📡 IP: {ngrok_ip}")
                        self.log_ekle(f"🔌 Port: {ngrok_port}")
                        
                        # GUI'yi güncelle
                        self.ngrok_bilgi_frame.pack(pady=10, padx=20, fill='x')
                        self.ngrok_ip_label.config(text=f"IP: {ngrok_ip}")
                        self.ngrok_port_label.config(text=f"Port: {ngrok_port}")
                        
                        self.durum_label.config(text="🟡 Bağlantı Bekleniyor...", fg='#f39c12')
                        
                        return
            except:
                pass
            
            time.sleep(1)
        
        self.log_ekle("⚠️ Ngrok bilgileri alınamadı, manuel kontrol edin")
    
    def panoya_kopyala(self, metin):
        """Metni panoya kopyala"""
        self.root.clipboard_clear()
        self.root.clipboard_append(metin)
        self.root.update()
        self.log_ekle(f"📋 Kopyalandı: {metin}")
        messagebox.showinfo("Kopyalandı", f"'{metin}' panoya kopyalandı!")
    
    def tumunu_kopyala(self):
        """IP ve Port'u birlikte kopyala"""
        ip = self.ngrok_ip_label.cget("text").replace("IP: ", "")
        port = self.ngrok_port_label.cget("text").replace("Port: ", "")
        metin = f"IP: {ip}\nPort: {port}"
        
        self.root.clipboard_clear()
        self.root.clipboard_append(metin)
        self.root.update()
        self.log_ekle(f"📋 Tüm bilgiler kopyalandı")
        messagebox.showinfo("Kopyalandı", "IP ve Port bilgileri kopyalandı!")
    
    def baglanti_kabul_et(self):
        """Gelen bağlantıyı kabul et"""
        try:
            self.baglanti, adres = self.server_socket.accept()
            self.bagli = True
            self.log_ekle(f"✅ Bağlantı kuruldu: {adres[0]}:{adres[1]}")
            self.durum_label.config(text="🟢 Bağlı - Konuşabilirsiniz!", fg='#2ecc71')
            self.kes_btn.config(state='normal')
            
            # Ses iletimini başlat
            self.ses_iletimi_baslat()
            
        except Exception as e:
            self.log_ekle(f"❌ Bağlantı hatası: {e}")
    
    def baglan(self):
        """Belirtilen IP ve porta bağlan"""
        try:
            ip = self.ip_entry.get().strip()
            port_str = self.port_entry.get().strip()
            
            if not ip or not port_str:
                messagebox.showerror("Hata", "IP ve Port alanlarını doldurun!")
                return
            
            port = int(port_str)
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.log_ekle(f"🔄 Bağlanılıyor: {ip}:{port}")
            
            self.client_socket.connect((ip, port))
            self.baglanti = self.client_socket
            self.bagli = True
            
            self.log_ekle(f"✅ Bağlantı başarılı!")
            self.durum_label.config(text="🟢 Bağlı - Konuşabilirsiniz!", fg='#2ecc71')
            
            self.sunucu_btn.config(state='disabled')
            self.baglan_btn.config(state='disabled')
            self.kes_btn.config(state='normal')
            
            # Ses iletimini başlat
            self.ses_iletimi_baslat()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Bağlantı kurulamadı: {e}")
            self.log_ekle(f"❌ Bağlantı hatası: {e}")
    
    def ses_iletimi_baslat(self):
        """Ses gönderme ve alma işlemlerini başlat"""
        self.dinleme_aktif = True
        
        # Ses gönderme thread'i
        threading.Thread(target=self.ses_gonder, daemon=True).start()
        
        # Ses alma thread'i
        threading.Thread(target=self.ses_al, daemon=True).start()
        
        self.log_ekle("🎤 Ses iletimi başladı")
    
    def ses_gonder(self):
        """Mikrofon sesini karşı tarafa gönder"""
        try:
            stream = self.audio.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    input=True,
                                    frames_per_buffer=self.CHUNK)
            
            while self.bagli and self.dinleme_aktif:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                if self.baglanti:
                    try:
                        self.baglanti.sendall(data)
                    except:
                        break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            self.log_ekle(f"❌ Ses gönderme hatası: {e}")
    
    def ses_al(self):
        """Karşı taraftan gelen sesi çal"""
        try:
            stream = self.audio.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    output=True,
                                    frames_per_buffer=self.CHUNK)
            
            while self.bagli and self.dinleme_aktif:
                try:
                    data = self.baglanti.recv(self.CHUNK)
                    if data:
                        stream.write(data)
                    else:
                        break
                except:
                    break
            
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            self.log_ekle(f"❌ Ses alma hatası: {e}")
    
    def ngrok_durdur(self):
        """Ngrok process'ini durdur"""
        if self.ngrok_process:
            try:
                self.ngrok_process.terminate()
                self.ngrok_process = None
                self.log_ekle("🛑 Ngrok durduruldu")
            except:
                pass
    
    def baglanti_kes(self):
        """Bağlantıyı sonlandır"""
        self.bagli = False
        self.dinleme_aktif = False
        
        if self.baglanti:
            self.baglanti.close()
        if self.server_socket:
            self.server_socket.close()
        if self.client_socket:
            self.client_socket.close()
        
        self.ngrok_durdur()
        self.ngrok_bilgi_frame.pack_forget()
        
        self.log_ekle("⚠️ Bağlantı kesildi")
        self.durum_label.config(text="⚪ Bağlantı Bekleniyor", fg='#ecf0f1')
        
        self.sunucu_btn.config(state='normal')
        self.baglan_btn.config(state='normal')
        self.kes_btn.config(state='disabled')
    
    def calistir(self):
        """Uygulamayı başlat"""
        self.root.protocol("WM_DELETE_WINDOW", self.kapat)
        self.root.mainloop()
    
    def kapat(self):
        """Uygulamayı kapat"""
        self.baglanti_kes()
        self.audio.terminate()
        self.root.destroy()

# Uygulamayı başlat
if __name__ == "__main__":
    print("🎙️ Sesli Konuşma Uygulaması (Ngrok Entegreli)")
    print("=" * 50)
    print("📦 Gerekli kütüphaneler:")
    print("   pip install pyaudio requests")
    print("\n🔧 Ngrok kurulumu:")
    print("   https://ngrok.com/download")
    print("\n💡 Auth Token:")
    print("   https://dashboard.ngrok.com/get-started/your-authtoken")
    print("=" * 50)
    
    try:
        uygulama = SesliKonusmaUygulamasi()
        uygulama.calistir()
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("\n💡 PyAudio kurulum:")
        print("Windows: pip install pipwin && pipwin install pyaudio")
        print("Mac: brew install portaudio && pip install pyaudio")
        print("Linux: sudo apt-get install python3-pyaudio")
