import socket
import pyaudio
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import re
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
        
        # Durum değişkenleri
        self.bagli = False
        self.dinleme_aktif = False
        
        # GUI oluştur
        self.pencere_olustur()
    
    def pencere_olustur(self):
        """Arayüz penceresi oluştur"""
        self.root = tk.Tk()
        self.root.title("🎙️ Sesli Konuşma Uygulaması")
        self.root.geometry("500x650")
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
        self.ip_entry = tk.Entry(baglanti_frame, width=25, font=('Arial', 11))
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Port
        tk.Label(baglanti_frame, text="Port:", 
                bg='#34495e', fg='white', font=('Arial', 11)).grid(row=1, column=0, sticky='w', pady=5)
        self.port_entry = tk.Entry(baglanti_frame, width=25, font=('Arial', 11))
        self.port_entry.insert(0, "5000")
        self.port_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Butonlar frame
        buton_frame = tk.Frame(self.root, bg='#2c3e50')
        buton_frame.pack(pady=20)
        
        # Sunucu olarak başlat butonu
        self.sunucu_btn = tk.Button(buton_frame, text="📡 Sunucu Olarak Başlat",
                                     command=self.sunucu_baslat,
                                     bg='#27ae60', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     width=20, height=2,
                                     cursor='hand2')
        self.sunucu_btn.grid(row=0, column=0, padx=10, pady=5)
        
        # Bağlan butonu
        self.baglan_btn = tk.Button(buton_frame, text="🔌 Bağlan",
                                     command=self.baglan,
                                     bg='#3498db', fg='white',
                                     font=('Arial', 12, 'bold'),
                                     width=20, height=2,
                                     cursor='hand2')
        self.baglan_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Bağlantıyı kes butonu
        self.kes_btn = tk.Button(buton_frame, text="❌ Bağlantıyı Kes",
                                  command=self.baglanti_kes,
                                  bg='#e74c3c', fg='white',
                                  font=('Arial', 12, 'bold'),
                                  width=20, height=2,
                                  cursor='hand2',
                                  state='disabled')
        self.kes_btn.grid(row=1, column=0, columnspan=2, pady=10)
        
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
        ngrok_frame = tk.Frame(self.root, bg='#9b59b6', padx=10, pady=8)
        ngrok_frame.pack(pady=5, padx=20, fill='x')
        
        ngrok_text = "💡 Farklı ağlardan bağlanmak için ngrok kullanın!\nKomut: ngrok tcp 5000"
        tk.Label(ngrok_frame, text=ngrok_text,
                bg='#9b59b6', fg='white',
                font=('Arial', 9), justify='left').pack()
        
        self.log_ekle("✅ Uygulama başlatıldı")
        self.log_ekle("ℹ️  Sunucu olarak başlatın veya bir IP'ye bağlanın")
        self.log_ekle("🌐 İnternet üzerinden bağlanmak için ngrok kullanabilirsiniz")
        self.log_ekle("✅ Uygulama başlatıldı")
        self.log_ekle("ℹ️  Sunucu olarak başlatın veya bir IP'ye bağlanın")
    
    def log_ekle(self, mesaj):
        """Log mesajı ekle"""
        import datetime
        zaman = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{zaman}] {mesaj}\n")
        self.log_text.see(tk.END)
    
    def sunucu_baslat(self):
        """Sunucu modunda başlat ve bağlantı bekle"""
        try:
            port = int(self.port_entry.get())
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            
            self.log_ekle(f"🎧 Sunucu başlatıldı - Port: {port}")
            self.log_ekle("⏳ Bağlantı bekleniyor...")
            self.durum_label.config(text="🟡 Bağlantı Bekleniyor...", fg='#f39c12')
            
            self.sunucu_btn.config(state='disabled')
            self.baglan_btn.config(state='disabled')
            
            # Arka planda bağlantı bekle
            threading.Thread(target=self.baglanti_kabul_et, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu başlatılamadı: {e}")
            self.log_ekle(f"❌ Hata: {e}")
    
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
            ip = self.ip_entry.get()
            port = int(self.port_entry.get())
            
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
    print("🎙️ Sesli Konuşma Uygulaması")
    print("=" * 40)
    print("📦 Gerekli: pip install pyaudio")
    print("\n🔧 Kullanım:")
    print("1. Bir bilgisayarda 'Sunucu Olarak Başlat'")
    print("2. Diğer bilgisayarda IP girerek 'Bağlan'")
    print("=" * 40)
    
    try:
        uygulama = SesliKonusmaUygulamasi()
        uygulama.calistir()
    except Exception as e:
        print(f"❌ Hata: {e}")
        print("\n💡 PyAudio kurulum:")
        print("Windows: pip install pipwin && pipwin install pyaudio")
        print("Mac: brew install portaudio && pip install pyaudio")
        print("Linux: sudo apt-get install python3-pyaudio")