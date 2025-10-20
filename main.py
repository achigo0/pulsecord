import socket
import pyaudio
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import re
import time
import requests

class BaglantiPenceresi:
    """Ngrok bağlantı bilgilerini gösteren popup pencere"""
    def __init__(self, parent, host, port):
        self.pencere = tk.Toplevel(parent)
        self.pencere.title("🌐 Bağlantı Bilgileri")
        self.pencere.geometry("500x400")
        self.pencere.configure(bg='#2c3e50')
        self.pencere.resizable(False, False)
        
        # Ana frame
        main_frame = tk.Frame(self.pencere, bg='#2c3e50', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Başlık
        baslik = tk.Label(main_frame, 
                         text="✅ Sunucu Başarıyla Başlatıldı!",
                         font=('Arial', 16, 'bold'),
                         bg='#2c3e50', fg='#2ecc71')
        baslik.pack(pady=(0, 20))
        
        # Bilgi metni
        bilgi = tk.Label(main_frame,
                        text="Bu bilgileri arkadaşınıza gönderin:",
                        font=('Arial', 11),
                        bg='#2c3e50', fg='#ecf0f1')
        bilgi.pack(pady=(0, 15))
        
        # IP Adresi Frame
        ip_frame = tk.Frame(main_frame, bg='#34495e', padx=20, pady=15)
        ip_frame.pack(fill='x', pady=5)
        
        tk.Label(ip_frame, text="IP Adresi:",
                font=('Arial', 10, 'bold'),
                bg='#34495e', fg='#bdc3c7').pack(anchor='w')
        
        ip_text_frame = tk.Frame(ip_frame, bg='#1a1a1a')
        ip_text_frame.pack(fill='x', pady=(5, 10))
        
        self.ip_label = tk.Label(ip_text_frame,
                                text=host,
                                font=('Courier', 14, 'bold'),
                                bg='#1a1a1a', fg='#3498db',
                                padx=10, pady=8)
        self.ip_label.pack(side='left', fill='x', expand=True)
        
        ip_copy_btn = tk.Button(ip_text_frame,
                               text="📋",
                               font=('Arial', 12),
                               bg='#3498db', fg='white',
                               command=lambda: self.kopyala(host, "IP"),
                               cursor='hand2',
                               width=3)
        ip_copy_btn.pack(side='right', padx=5)
        
        # Port Frame
        port_frame = tk.Frame(main_frame, bg='#34495e', padx=20, pady=15)
        port_frame.pack(fill='x', pady=5)
        
        tk.Label(port_frame, text="Port:",
                font=('Arial', 10, 'bold'),
                bg='#34495e', fg='#bdc3c7').pack(anchor='w')
        
        port_text_frame = tk.Frame(port_frame, bg='#1a1a1a')
        port_text_frame.pack(fill='x', pady=(5, 10))
        
        self.port_label = tk.Label(port_text_frame,
                                  text=port,
                                  font=('Courier', 14, 'bold'),
                                  bg='#1a1a1a', fg='#e74c3c',
                                  padx=10, pady=8)
        self.port_label.pack(side='left', fill='x', expand=True)
        
        port_copy_btn = tk.Button(port_text_frame,
                                 text="📋",
                                 font=('Arial', 12),
                                 bg='#e74c3c', fg='white',
                                 command=lambda: self.kopyala(port, "Port"),
                                 cursor='hand2',
                                 width=3)
        port_copy_btn.pack(side='right', padx=5)
        
        # Tam URL Frame
        full_url = f"{host}:{port}"
        url_frame = tk.Frame(main_frame, bg='#34495e', padx=20, pady=15)
        url_frame.pack(fill='x', pady=5)
        
        tk.Label(url_frame, text="Tam Adres:",
                font=('Arial', 10, 'bold'),
                bg='#34495e', fg='#bdc3c7').pack(anchor='w')
        
        url_text_frame = tk.Frame(url_frame, bg='#1a1a1a')
        url_text_frame.pack(fill='x', pady=(5, 10))
        
        self.url_label = tk.Label(url_text_frame,
                                 text=full_url,
                                 font=('Courier', 12, 'bold'),
                                 bg='#1a1a1a', fg='#f39c12',
                                 padx=10, pady=8)
        self.url_label.pack(side='left', fill='x', expand=True)
        
        url_copy_btn = tk.Button(url_text_frame,
                                text="📋",
                                font=('Arial', 12),
                                bg='#f39c12', fg='white',
                                command=lambda: self.kopyala(full_url, "Tam Adres"),
                                cursor='hand2',
                                width=3)
        url_copy_btn.pack(side='right', padx=5)
        
        # Büyük kopyalama butonu
        big_copy_btn = tk.Button(main_frame,
                                text="📋 Tüm Bilgileri Kopyala",
                                font=('Arial', 12, 'bold'),
                                bg='#27ae60', fg='white',
                                command=lambda: self.kopyala(f"IP: {host}\nPort: {port}", "Tüm Bilgiler"),
                                cursor='hand2',
                                padx=20, pady=10)
        big_copy_btn.pack(pady=20)
        
        # Kapat butonu
        kapat_btn = tk.Button(main_frame,
                             text="Kapat",
                             font=('Arial', 10),
                             bg='#95a5a6', fg='white',
                             command=self.pencere.destroy,
                             cursor='hand2',
                             width=15)
        kapat_btn.pack(pady=(0, 10))
        
        # Pencereyi ortala
        self.pencere.transient(parent)
        self.pencere.grab_set()
        
    def kopyala(self, text, tip):
        """Metni panoya kopyala"""
        self.pencere.clipboard_clear()
        self.pencere.clipboard_append(text)
        self.pencere.update()
        
        # Geçici bildirim
        bildirim = tk.Toplevel(self.pencere)
        bildirim.title("")
        bildirim.geometry("250x80")
        bildirim.configure(bg='#27ae60')
        bildirim.overrideredirect(True)
        
        # Pencereyi ortala
        x = self.pencere.winfo_x() + (self.pencere.winfo_width() // 2) - 125
        y = self.pencere.winfo_y() + (self.pencere.winfo_height() // 2) - 40
        bildirim.geometry(f"+{x}+{y}")
        
        tk.Label(bildirim,
                text=f"✅ {tip} Kopyalandı!",
                font=('Arial', 12, 'bold'),
                bg='#27ae60', fg='white').pack(expand=True)
        
        # 1.5 saniye sonra kapat
        bildirim.after(1500, bildirim.destroy)


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
        self.ngrok_process = None
        self.ngrok_url = None
        
        # GUI oluştur
        self.pencere_olustur()
    
    def pencere_olustur(self):
        """Ana pencereyi oluştur"""
        self.root = tk.Tk()
        self.root.title("🎙️ Sesli Konuşma Uygulaması")
        self.root.geometry("550x700")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Başlık
        baslik_frame = tk.Frame(self.root, bg='#34495e', pady=15)
        baslik_frame.pack(fill='x')
        
        baslik = tk.Label(baslik_frame, 
                         text="🎙️ Sesli Konuşma Uygulaması", 
                         font=('Arial', 18, 'bold'), 
                         bg='#34495e', fg='white')
        baslik.pack()
        
        tk.Label(baslik_frame,
                text="İnternet üzerinden gerçek zamanlı ses iletişimi",
                font=('Arial', 9),
                bg='#34495e', fg='#bdc3c7').pack()
        
        # Sunucu bölümü
        sunucu_frame = tk.LabelFrame(self.root, 
                                     text="  🌐 SUNUCU MODU  ",
                                     font=('Arial', 12, 'bold'),
                                     bg='#2c3e50', fg='#3498db',
                                     padx=20, pady=15)
        sunucu_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(sunucu_frame,
                text="Arkadaşlarınızın size bağlanmasını sağlayın",
                font=('Arial', 9),
                bg='#2c3e50', fg='#bdc3c7').pack(pady=(0, 10))
        
        self.ngrok_btn = tk.Button(sunucu_frame, 
                                   text="🚀 Ngrok ile Sunucu Başlat",
                                   command=self.ngrok_ile_baslat,
                                   bg='#9b59b6', fg='white',
                                   font=('Arial', 12, 'bold'),
                                   cursor='hand2',
                                   height=2)
        self.ngrok_btn.pack(fill='x', pady=5)
        
        tk.Label(sunucu_frame,
                text="⚡ Port yönlendirmeye gerek yok!",
                font=('Arial', 8),
                bg='#2c3e50', fg='#f39c12').pack(pady=(5, 0))
        
        # İstemci bölümü
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
        
        # IP girişi
        ip_giris_frame = tk.Frame(istemci_frame, bg='#2c3e50')
        ip_giris_frame.pack(fill='x', pady=5)
        
        tk.Label(ip_giris_frame, text="IP Adresi:", 
                bg='#2c3e50', fg='white', 
                font=('Arial', 10)).pack(side='left', padx=(0, 10))
        
        self.ip_entry = tk.Entry(ip_giris_frame, 
                                font=('Courier', 11),
                                bg='#34495e', fg='white',
                                insertbackground='white',
                                relief='flat',
                                width=30)
        self.ip_entry.pack(side='left', ipady=5)
        self.ip_entry.insert(0, "0.tcp.ngrok.io")
        
        # Port girişi
        port_giris_frame = tk.Frame(istemci_frame, bg='#2c3e50')
        port_giris_frame.pack(fill='x', pady=5)
        
        tk.Label(port_giris_frame, text="Port:", 
                bg='#2c3e50', fg='white', 
                font=('Arial', 10)).pack(side='left', padx=(0, 10))
        
        self.port_entry = tk.Entry(port_giris_frame, 
                                   font=('Courier', 11),
                                   bg='#34495e', fg='white',
                                   insertbackground='white',
                                   relief='flat',
                                   width=30)
        self.port_entry.pack(side='left', ipady=5)
        self.port_entry.insert(0, "12345")
        
        # Bağlan butonu
        self.baglan_btn = tk.Button(istemci_frame, 
                                    text="🔌 Bağlan",
                                    command=self.baglan,
                                    bg='#3498db', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    cursor='hand2',
                                    height=2)
        self.baglan_btn.pack(fill='x', pady=(10, 5))
        
        # Durum bölümü
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
        
        # Kes butonu
        self.kes_btn = tk.Button(self.root, 
                                text="❌ Bağlantıyı Kes",
                                command=self.baglanti_kes,
                                bg='#e74c3c', fg='white',
                                font=('Arial', 11, 'bold'),
                                cursor='hand2',
                                height=2,
                                state='disabled')
        self.kes_btn.pack(pady=10, padx=20, fill='x')
        
        # Log alanı
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
                                                   relief='flat')
        self.log_text.pack(fill='both', expand=True)
        
        self.log_ekle("✅ Uygulama başlatıldı")
        self.log_ekle("ℹ️  Ngrok ile sunucu başlatın veya bir adrese bağlanın")
    
    def log_ekle(self, mesaj):
        """Log mesajı ekle"""
        import datetime
        zaman = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{zaman}] {mesaj}\n")
        self.log_text.see(tk.END)
    
    def ngrok_ile_baslat(self):
        """Ngrok ile sunucu başlat"""
        try:
            port = 5000  # Sabit port kullan
            
            self.log_ekle("🚀 Ngrok başlatılıyor...")
            self.durum_label.config(text="🟡 Ngrok başlatılıyor...", fg='#f39c12')
            
            # Önce yerel sunucuyu başlat
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            
            self.log_ekle(f"✅ Yerel sunucu başlatıldı - Port: {port}")
            
            # Ngrok'u başlat
            try:
                self.ngrok_process = subprocess.Popen(
                    ['ngrok', 'tcp', str(port)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self.log_ekle("⏳ Ngrok URL'i alınıyor...")
                
                # Butonları devre dışı bırak
                self.ngrok_btn.config(state='disabled')
                self.baglan_btn.config(state='disabled')
                
                # Ngrok URL'ini al ve popup göster
                threading.Thread(target=self.ngrok_url_al_ve_goster, daemon=True).start()
                
                # Bağlantı bekle
                threading.Thread(target=self.baglanti_kabul_et, daemon=True).start()
                
            except FileNotFoundError:
                messagebox.showerror("Ngrok Bulunamadı", 
                    "Ngrok yüklü değil!\n\n"
                    "Kurulum Adımları:\n"
                    "1. https://ngrok.com/download\n"
                    "2. Üye olun ve auth token alın\n"
                    "3. ngrok config add-authtoken <TOKEN>\n"
                    "4. Ngrok'u PATH'e ekleyin")
                self.log_ekle("❌ Ngrok bulunamadı!")
                self.durum_label.config(text="⚪ Beklemede", fg='#ecf0f1')
                if self.server_socket:
                    self.server_socket.close()
                self.ngrok_btn.config(state='normal')
                self.baglan_btn.config(state='normal')
                
        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu başlatılamadı:\n{e}")
            self.log_ekle(f"❌ Hata: {e}")
            self.durum_label.config(text="⚪ Beklemede", fg='#ecf0f1')
            self.ngrok_btn.config(state='normal')
            self.baglan_btn.config(state='normal')
    
    def ngrok_url_al_ve_goster(self):
        """Ngrok URL'ini al ve popup pencerede göster"""
        max_deneme = 15
        for i in range(max_deneme):
            try:
                time.sleep(2)
                response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                data = response.json()
                
                if data.get('tunnels') and len(data['tunnels']) > 0:
                    tunnel_url = data['tunnels'][0]['public_url']
                    match = re.search(r'tcp://(.+):(\d+)', tunnel_url)
                    
                    if match:
                        host = match.group(1)
                        port = match.group(2)
                        
                        self.log_ekle("=" * 50)
                        self.log_ekle(f"🎉 Ngrok Başarıyla Başlatıldı!")
                        self.log_ekle(f"📍 IP: {host}")
                        self.log_ekle(f"📍 Port: {port}")
                        self.log_ekle("=" * 50)
                        
                        self.durum_label.config(
                            text="🟡 Bağlantı Bekleniyor...", 
                            fg='#f39c12'
                        )
                        
                        # Popup pencereyi göster
                        self.root.after(0, lambda: BaglantiPenceresi(self.root, host, port))
                        return
                        
            except Exception as e:
                if i == max_deneme - 1:
                    self.log_ekle(f"⚠️ Ngrok URL alınamadı: {e}")
                    self.log_ekle("💡 localhost:4040'ta kontrol edin")
        
        self.log_ekle("⚠️ Ngrok URL otomatik alınamadı")
        self.log_ekle("💡 Tarayıcıda http://localhost:4040 adresini açın")
    
    def baglanti_kabul_et(self):
        """Gelen bağlantıyı kabul et"""
        try:
            self.log_ekle("⏳ Bağlantı bekleniyor...")
            self.baglanti, adres = self.server_socket.accept()
            self.bagli = True
            
            self.log_ekle(f"✅ Bağlantı kuruldu: {adres[0]}:{adres[1]}")
            self.durum_label.config(text="🟢 Bağlı - Konuşabilirsiniz!", fg='#2ecc71')
            self.kes_btn.config(state='normal')
            
            # Ses iletimini başlat
            self.ses_iletimi_baslat()
            
        except Exception as e:
            if self.bagli:  # Sadece beklenmeyen hatalarda log
                self.log_ekle(f"❌ Bağlantı hatası: {e}")
    
    def baglan(self):
        """Belirtilen adrese bağlan"""
        try:
            ip = self.ip_entry.get().strip()
            port = int(self.port_entry.get().strip())
            
            if not ip or not port:
                messagebox.showwarning("Uyarı", "IP ve Port bilgilerini girin!")
                return
            
            self.log_ekle(f"🔄 Bağlanılıyor: {ip}:{port}")
            self.durum_label.config(text="🟡 Bağlanılıyor...", fg='#f39c12')
            
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(10)
            self.client_socket.connect((ip, port))
            
            self.baglanti = self.client_socket
            self.bagli = True
            
            self.log_ekle(f"✅ Bağlantı başarılı!")
            self.durum_label.config(text="🟢 Bağlı - Konuşabilirsiniz!", fg='#2ecc71')
            
            self.ngrok_btn.config(state='disabled')
            self.baglan_btn.config(state='disabled')
            self.kes_btn.config(state='normal')
            
            # Ses iletimini başlat
            self.ses_iletimi_baslat()
            
        except socket.timeout:
            messagebox.showerror("Zaman Aşımı", "Bağlantı zaman aşımına uğradı!\nSunucu çalışıyor mu?")
            self.log_ekle("❌ Bağlantı zaman aşımı")
            self.durum_label.config(text="⚪ Beklemede", fg='#ecf0f1')
        except Exception as e:
            messagebox.showerror("Bağlantı Hatası", f"Bağlantı kurulamadı:\n{e}")
            self.log_ekle(f"❌ Bağlantı hatası: {e}")
            self.durum_label.config(text="⚪ Beklemede", fg='#ecf0f1')
    
    def ses_iletimi_baslat(self):
        """Ses gönderme ve alma işlemlerini başlat"""
        self.dinleme_aktif = True
        threading.Thread(target=self.ses_gonder, daemon=True).start()
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
            try:
                self.baglanti.close()
            except:
                pass
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
        
        # Ngrok'u kapat
        if self.ngrok_process:
            self.ngrok_process.terminate()
            self.ngrok_process = None
            self.log_ekle("🔴 Ngrok kapatıldı")
        
        self.log_ekle("⚠️ Bağlantı kesildi")
        self.durum_label.config(text="⚪ Beklemede", fg='#ecf0f1')
        
        self.ngrok_btn.config(state='normal')
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


if __name__ == "__main__":
    print("=" * 60)
    print("🎙️  SESLİ KONUŞMA UYGULAMASI - NGROK ENTEGRELİ")
    print("=" * 60)
    print("\n📦 Gereksinimler:")
    print("   pip install pyaudio requests")
    print("\n🌐 Ngrok Kurulumu:")
    print("   1. https://ngrok.com/download")
    print("   2. Üye olun ve auth token alın")
    print("   3. ngrok config add-authtoken <YOUR_TOKEN>")
    print("\n🚀 Kullanım:")
    print("   • Sunucu: 'Ngrok ile Sunucu Başlat' butonuna tıklayın")
    print("   • İstemci: IP ve Port girerek 'Bağlan' butonuna tıklayın")
    print("=" * 60)
    print()
    try:
        uygulama = SesliKonusmaUygulamasi()
        uygulama.calistir()
    except KeyboardInterrupt:
        print("\n⚠️  Uygulama kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Kritik Hata: {e}")
        print("\n💡 PyAudio kurulum sorunları için:")
        print("   Windows: pip install pipwin && pipwin install pyaudio")
        print("   Mac: brew install portaudio && pip install pyaudio")
        print("   Linux: sudo apt-get install python3-pyaudio")
