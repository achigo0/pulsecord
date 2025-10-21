import asyncio
import websockets
import pyaudio
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import json
import os
import time
import requests
from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

class AyarlarPenceresi:
    """Ngrok token ve diğer ayarları yöneten pencere"""
    def __init__(self, parent):
        self.pencere = tk.Toplevel(parent)
        self.pencere.title("⚙️ Ayarlar")
        self.pencere.geometry("600x400")
        self.pencere.configure(bg='#2c3e50')
        self.pencere.resizable(False, False)
        
        main_frame = tk.Frame(self.pencere, bg='#2c3e50', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        baslik = tk.Label(main_frame, 
                         text="⚙️ Uygulama Ayarları",
                         font=('Arial', 18, 'bold'),
                         bg='#2c3e50', fg='white')
        baslik.pack(pady=(0, 20))
        
        # Ngrok Token
        token_frame = tk.LabelFrame(main_frame,
                                    text="  🔑 Ngrok Auth Token  ",
                                    font=('Arial', 11, 'bold'),
                                    bg='#2c3e50', fg='#3498db',
                                    padx=20, pady=15)
        token_frame.pack(fill='x', pady=10)
        
        tk.Label(token_frame,
                text="Token'ınızı https://dashboard.ngrok.com/get-started/your-authtoken\nadresinden alabilirsiniz.",
                font=('Arial', 9),
                bg='#2c3e50', fg='#bdc3c7',
                justify='left').pack(anchor='w', pady=(0, 10))
        
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
        
        # Butonlar
        buton_frame = tk.Frame(main_frame, bg='#2c3e50')
        buton_frame.pack(pady=(20, 0))
        
        tk.Button(buton_frame,
                 text="Kapat",
                 font=('Arial', 11),
                 bg='#95a5a6', fg='white',
                 command=self.pencere.destroy,
                 cursor='hand2',
                 width=15).pack(side='left', padx=5)
        
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
            config = {'ngrok_token': token}
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
            
            result = subprocess.run(['ngrok', 'config', 'add-authtoken', token],
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Başarılı", "✅ Token başarıyla kaydedildi!")
            else:
                messagebox.showerror("Hata", f"Token kaydedilemedi:\n{result.stderr}")
                
        except FileNotFoundError:
            messagebox.showerror("Ngrok Bulunamadı",
                "Ngrok yüklü değil!\n\nKurulum: https://ngrok.com/download")
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen hata:\n{e}")


class BaglantiPenceresi:
    """WebSocket bağlantı bilgilerini gösteren popup"""
    def __init__(self, parent, ws_url):
        self.pencere = tk.Toplevel(parent)
        self.pencere.title("🌐 Bağlantı Bilgileri")
        self.pencere.geometry("500x300")
        self.pencere.configure(bg='#2c3e50')
        self.pencere.resizable(False, False)
        
        main_frame = tk.Frame(self.pencere, bg='#2c3e50', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        baslik = tk.Label(main_frame, 
                         text="✅ Sunucu Başarıyla Başlatıldı!",
                         font=('Arial', 16, 'bold'),
                         bg='#2c3e50', fg='#2ecc71')
        baslik.pack(pady=(0, 20))
        
        bilgi = tk.Label(main_frame,
                        text="Bu URL'yi arkadaşınıza gönderin:",
                        font=('Arial', 11),
                        bg='#2c3e50', fg='#ecf0f1')
        bilgi.pack(pady=(0, 15))
        
        # URL Frame
        url_frame = tk.Frame(main_frame, bg='#34495e', padx=20, pady=15)
        url_frame.pack(fill='x', pady=5)
        
        tk.Label(url_frame, text="WebSocket URL:",
                font=('Arial', 10, 'bold'),
                bg='#34495e', fg='#bdc3c7').pack(anchor='w')
        
        url_text_frame = tk.Frame(url_frame, bg='#1a1a1a')
        url_text_frame.pack(fill='x', pady=(5, 10))
        
        self.url_label = tk.Label(url_text_frame,
                                 text=ws_url,
                                 font=('Courier', 10, 'bold'),
                                 bg='#1a1a1a', fg='#3498db',
                                 padx=10, pady=8,
                                 wraplength=400)
        self.url_label.pack(side='left', fill='x', expand=True)
        
        url_copy_btn = tk.Button(url_text_frame,
                                text="📋",
                                font=('Arial', 12),
                                bg='#3498db', fg='white',
                                command=lambda: self.kopyala(ws_url),
                                cursor='hand2',
                                width=3)
        url_copy_btn.pack(side='right', padx=5)
        
        # Büyük kopyalama butonu
        big_copy_btn = tk.Button(main_frame,
                                text="📋 URL'yi Kopyala",
                                font=('Arial', 12, 'bold'),
                                bg='#27ae60', fg='white',
                                command=lambda: self.kopyala(ws_url),
                                cursor='hand2',
                                padx=20, pady=10)
        big_copy_btn.pack(pady=20)
        
        kapat_btn = tk.Button(main_frame,
                             text="Kapat",
                             font=('Arial', 10),
                             bg='#95a5a6', fg='white',
                             command=self.pencere.destroy,
                             cursor='hand2',
                             width=15)
        kapat_btn.pack(pady=(0, 10))
        
        self.pencere.transient(parent)
        self.pencere.grab_set()
        
    def kopyala(self, text):
        self.pencere.clipboard_clear()
        self.pencere.clipboard_append(text)
        self.pencere.update()
        
        bildirim = tk.Toplevel(self.pencere)
        bildirim.title("")
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
        # Ses ayarları
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        
        self.audio = pyaudio.PyAudio()
        
        # WebSocket değişkenleri
        self.ws_server = None
        self.ws_client = None
        self.connected_clients = set()
        self.bagli = False
        self.ngrok_process = None
        
        # Asyncio loop
        self.loop = None
        self.server_task = None
        
        self.pencere_olustur()
    
    def pencere_olustur(self):
        self.root = tk.Tk()
        self.root.title("🎙️ Sesli Konuşma - WebSocket")
        self.root.geometry("600x700")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Menü
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        ayarlar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Ayarlar", menu=ayarlar_menu)
        ayarlar_menu.add_command(label="Ngrok Token", command=self.ayarlar_ac)
        ayarlar_menu.add_separator()
        ayarlar_menu.add_command(label="Çıkış", command=self.kapat)
        
        # Başlık
        baslik_frame = tk.Frame(self.root, bg='#34495e', pady=15)
        baslik_frame.pack(fill='x')
        
        baslik = tk.Label(baslik_frame, 
                         text="🎙️ Sesli Konuşma - WebSocket", 
                         font=('Arial', 18, 'bold'), 
                         bg='#34495e', fg='white')
        baslik.pack()
        
        tk.Label(baslik_frame,
                text="HTTP WebSocket üzerinden ses iletişimi (Ngrok Free ✅)",
                font=('Arial', 9),
                bg='#34495e', fg='#2ecc71').pack()
        
        # Ayarlar butonu
        ayar_btn = tk.Button(baslik_frame,
                            text="⚙️",
                            font=('Arial', 14),
                            bg='#34495e', fg='white',
                            command=self.ayarlar_ac,
                            cursor='hand2',
                            relief='flat',
                            width=3)
        ayar_btn.place(relx=0.95, rely=0.5, anchor='e')
        
        # Sunucu bölümü
        sunucu_frame = tk.LabelFrame(self.root, 
                                     text="  🌐 SUNUCU MODU  ",
                                     font=('Arial', 12, 'bold'),
                                     bg='#2c3e50', fg='#3498db',
                                     padx=20, pady=15)
        sunucu_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(sunucu_frame,
                text="WebSocket sunucusu başlatın (Ngrok Free ile çalışır!)",
                font=('Arial', 9),
                bg='#2c3e50', fg='#bdc3c7').pack(pady=(0, 10))
        
        self.sunucu_btn = tk.Button(sunucu_frame, 
                                   text="🚀 WebSocket Sunucusu Başlat",
                                   command=self.sunucu_baslat,
                                   bg='#9b59b6', fg='white',
                                   font=('Arial', 12, 'bold'),
                                   cursor='hand2',
                                   height=2)
        self.sunucu_btn.pack(fill='x', pady=5)
        
        tk.Label(sunucu_frame,
                text="✅ Ngrok ücretsiz versiyonu ile uyumlu!",
                font=('Arial', 8),
                bg='#2c3e50', fg='#2ecc71').pack(pady=(5, 0))
        
        # İstemci bölümü
        istemci_frame = tk.LabelFrame(self.root, 
                                      text="  🔌 İSTEMCİ MODU  ",
                                      font=('Arial', 12, 'bold'),
                                      bg='#2c3e50', fg='#2ecc71',
                                      padx=20, pady=15)
        istemci_frame.pack(pady=15, padx=20, fill='x')
        
        tk.Label(istemci_frame,
                text="Arkadaşınızın WebSocket URL'sine bağlanın",
                font=('Arial', 9),
                bg='#2c3e50', fg='#bdc3c7').pack(pady=(0, 10))
        
        # URL girişi
        url_giris_frame = tk.Frame(istemci_frame, bg='#2c3e50')
        url_giris_frame.pack(fill='x', pady=5)
        
        tk.Label(url_giris_frame, text="WebSocket URL:", 
                bg='#2c3e50', fg='white', 
                font=('Arial', 10)).pack(anchor='w', padx=(0, 10))
        
        self.url_entry = tk.Entry(url_giris_frame, 
                                font=('Courier', 10),
                                bg='#34495e', fg='white',
                                insertbackground='white',
                                relief='flat')
        self.url_entry.pack(fill='x', ipady=5)
        self.url_entry.insert(0, "wss://example.ngrok.io")
        
        # Bağlan butonu
        self.baglan_btn = tk.Button(istemci_frame, 
                                    text="🔌 Bağlan",
                                    command=self.baglan,
                                    bg='#3498db', fg='white',
                                    font=('Arial', 12, 'bold'),
                                    cursor='hand2',
                                    height=2)
        self.baglan_btn.pack(fill='x', pady=(10, 5))
        
        # Durum
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
        
        # Log
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
        
        self.log_ekle("✅ Uygulama başlatıldı - WebSocket modu", "SUCCESS")
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
        """WebSocket sunucusunu başlat"""
        self.log_ekle("🚀 WebSocket sunucusu başlatılıyor...", "INFO")
        
        # Asyncio loop'u yeni thread'de başlat
        threading.Thread(target=self.ws_sunucu_calistir, daemon=True).start()
        
        # Ngrok'u başlat
        time.sleep(2)
        threading.Thread(target=self.ngrok_baslat, daemon=True).start()
        
        self.sunucu_btn.config(state='disabled')
        self.baglan_btn.config(state='disabled')
        self.durum_label.config(text="🟡 Sunucu hazırlanıyor...", fg='#f39c12')
    
    def ws_sunucu_calistir(self):
        """WebSocket sunucusunu async olarak çalıştır"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        async def handler(websocket, path):
            self.log_ekle(f"✅ Yeni bağlantı: {websocket.remote_address}", "SUCCESS")
            self.connected_clients.add(websocket)
            self.bagli = True
            self.root.after(0, lambda: self.durum_label.config(text="🟢 Bağlı - Konuşabilirsiniz!", fg='#2ecc71'))
            self.root.after(0, lambda: self.kes_btn.config(state='normal'))
            
            # Ses akışı başlat
            threading.Thread(target=self.ses_gonder_ws, args=(websocket,), daemon=True).start()
            
            try:
                async for message in websocket:
                    # Gelen ses verisini çal
                    threading.Thread(target=self.ses_cal, args=(message,), daemon=True).start()
            except websockets.exceptions.ConnectionClosed:
                self.log_ekle("⚠️ Bağlantı kapandı", "WARNING")
            finally:
                self.connected_clients.remove(websocket)
                if not self.connected_clients:
                    self.bagli = False
                    self.root.after(0, lambda: self.durum_label.config(text="⚪ Beklemede", fg='#ecf0f1'))
        
        start_server = websockets.serve(handler, "0.0.0.0", 8765)
        
        self.log_ekle("✅ WebSocket sunucusu başlatıldı - ws://0.0.0.0:8765", "SUCCESS")
        
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()
    
    def ngrok_baslat(self):
        """Ngrok HTTP tünelini başlat"""
        try:
            self.log_ekle("🌐 Ngrok HTTP tüneli başlatılıyor...", "INFO")
            
            self.ngrok_process = subprocess.Popen(
                ['ngrok', 'http', '8765'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            time.sleep(3)
            
            # Ngrok URL'ini al
            max_deneme = 10
            for i in range(max_deneme):
                try:
                    response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                    data = response.json()
                    
                    if data.get('tunnels'):
                        # HTTPS URL'ini al
                        for tunnel in data['tunnels']:
                            url = tunnel['public_url']
                            if url.startswith('https://'):
                                # WebSocket URL'e çevir
                                ws_url = url.replace('https://', 'wss://')
                                
                                self.log_ekle("=" * 50, "SUCCESS")
                                self.log_ekle(f"🎉 NGROK BAŞARIYLA BAŞLATILDI!", "SUCCESS")
                                self.log_ekle(f"🔗 WebSocket URL: {ws_url}", "SUCCESS")
                                self.log_ekle("=" * 50, "SUCCESS")
                                
                                # Popup göster
                                self.root.after(0, lambda: BaglantiPenceresi(self.root, ws_url))
                                self.root.after(0, lambda: self.durum_label.config(text="🟡 Bağlantı bekleniyor...", fg='#f39c12'))
                                return
                                
                except:
                    time.sleep(2)
            
            self.log_ekle("❌ Ngrok URL alınamadı", "ERROR")
            
        except FileNotFoundError:
            self.log_ekle("❌ Ngrok bulunamadı!", "ERROR")
            messagebox.showerror("Hata", "Ngrok yüklü değil!\n\nhttps://ngrok.com/download")
        except Exception as e:
            self.log_ekle(f"❌ Ngrok hatası: {e}", "ERROR")
    
    def baglan(self):
        """WebSocket'e istemci olarak bağlan"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Uyarı", "WebSocket URL giriniz!")
            return
        
        self.log_ekle(f"🔄 Bağlanılıyor: {url}", "INFO")
        self.durum_label.config(text="🟡 Bağlanılıyor...", fg='#f39c12')
        
        threading.Thread(target=self.ws_istemci_baglan, args=(url,), daemon=True).start()
        
        self.sunucu_btn.config(state='disabled')
        self.baglan_btn.config(state='disabled')
    
    def ws_istemci_baglan(self, url):
        """WebSocket istemcisi olarak bağlan"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def connect():
            try:
                async with websockets.connect(url) as websocket:
                    self.ws_client = websocket
                    self.bagli = True
                    
                    self.log_ekle("✅ Bağlantı başarılı!", "SUCCESS")
                    self.root.after(0, lambda: self.durum_label.config(text="🟢 Bağlı - Konuşabilirsiniz!", fg='#2ecc71'))
                    self.root.after(0, lambda: self.kes_btn.config(state='normal'))
                    
                    # Ses gönder
                    threading.Thread(target=self.ses_gonder_ws, args=(websocket,), daemon=True).start()
                    
                    # Ses al
                    async for message in websocket:
                        threading.Thread(target=self.ses_cal, args=(message,), daemon=True).start()
                        
            except Exception as e:
                self.log_ekle(f"❌ Bağlantı hatası: {e}", "ERROR")
                self.root.after(0, lambda: messagebox.showerror("Hata", f"Bağlanamadı:\n{e}"))
                self.root.after(0, lambda: self.durum_label.config(text="⚪ Beklemede", fg='#ecf0f1'))
                self.root.after(0, lambda: self.baglan_btn.config(state='normal'))
        
        loop.run_until_complete(connect())
    
    def ses_gonder_ws(self, websocket):
        """Mikrofon sesini WebSocket üzerinden gönder"""
        try:
            stream = self.audio.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    input=True,
                                    frames_per_buffer=self.CHUNK)
            
            self.log_ekle("🎤 Mikrofon aktif", "SUCCESS")
            
            while self.bagli:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                try:
                    asyncio.run_coroutine_threadsafe(websocket.send(data), self.loop or asyncio.get_event_loop())
                except:
                    break
            
            stream.stop_stream()
            stream.close()
            self.log_ekle("🛑 Mikrofon durduruldu", "INFO")
            
        except Exception as e:
            self.log_ekle(f"❌ Mikrofon hatası: {e}", "ERROR")
    
    def ses_cal(self, data):
        """Gelen ses verisini çal"""
        try:
            stream = self.audio.open(format=self.FORMAT,
                                    channels=self.CHANNELS,
                                    rate=self.RATE,
                                    output=True,
                                    frames_per_buffer=self.CHUNK)
            
            stream.write(data)
            stream.stop_stream()
            stream.close()
            
        except Exception as e:
            self.log_ekle(f"❌ Ses çalma hatası: {e}", "ERROR")
    
    def baglanti_kes(self):
        """Bağlantıyı kes"""
        self.log_ekle("🔴 Bağlantı kesiliyor...", "WARNING")
        
        self.bagli = False
        
        if self.ws_client:
            try:
                asyncio.run_coroutine_threadsafe(self.ws_client.close(), asyncio.get_event_loop())
            except:
                pass
        
        if self.ngrok_process:
            try:
                self.ngrok_process.terminate()
                self.log_ekle("🔴 Ngrok durduruldu", "WARNING")
            except:
                pass
        
        if self.loop:
            try:
                self.loop.call_soon_threadsafe(self.loop.stop)
            except:
                pass
        
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
    print("🎙️  SESLİ KONUŞMA - WEBSOCKET (NGROK FREE)")
    print("=" * 60)
    print("\n📦 Gereksinimler:")
    print("   pip install pyaudio websockets requests")
    print("\n🌐 Ngrok Kurulumu:")
    print("   1. https://ngrok.com/download")
    print("   2. Üye olun ve auth token alın")
    print("   3. Uygulamada Ayarlar > Ngrok Token")
    print("\n✅ Ngrok FREE ile çalışır (HTTP/WebSocket)!")
    print("\n🚀 Kullanım:")
    print("   • Sunucu: 'WebSocket Sunucusu Başlat'")
    print("   • İstemci: WebSocket URL girerek 'Bağlan'")
    print("=" * 60)
    print()
    
    try:
        uygulama = SesliKonusmaUygulamasi()
        uygulama.calistir()
    except KeyboardInterrupt:
        print("\n⚠️  Kullanıcı tarafından durduruldu")
    except Exception as e:
        print(f"\n❌ Hata: {e}")
