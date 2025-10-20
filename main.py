import socket
import pyaudio
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
import subprocess
import re
import time
import requests
import os
import json

class AyarlarPenceresi:
    """Ngrok token ve diğer ayarları yöneten pencere"""
    def __init__(self, parent):
        self.pencere = tk.Toplevel(parent)
        self.pencere.title("⚙️ Ayarlar")
        self.pencere.geometry("600x500")
        self.pencere.configure(bg='#2c3e50')
        self.pencere.resizable(False, False)
        
        # Ana frame
        main_frame = tk.Frame(self.pencere, bg='#2c3e50', padx=30, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Başlık
        baslik = tk.Label(main_frame, 
                         text="⚙️ Uygulama Ayarları",
                         font=('Arial', 18, 'bold'),
                         bg='#2c3e50', fg='white')
        baslik.pack(pady=(0, 20))
        
        # Ngrok Token Bölümü
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
        
        # Token girişi
        token_giris_frame = tk.Frame(token_frame, bg='#2c3e50')
        token_giris_frame.pack(fill='x', pady=5)
        
        self.token_entry = tk.Entry(token_giris_frame,
                                    font=('Courier', 10),
                                    bg='#34495e', fg='white',
                                    insertbackground='white',
                                    show='*',
                                    relief='flat')
        self.token_entry.pack(side='left', fill='x', expand=True, ipady=8)
        
        # Token'ı göster/gizle butonu
        self.goster_btn = tk.Button(token_giris_frame,
                                    text="👁️",
                                    font=('Arial', 10),
                                    bg='#34495e', fg='white',
                                    command=self.token_goster_gizle,
                                    cursor='hand2',
                                    width=3)
        self.goster_btn.pack(side='right', padx=(5, 0))
        
        # Mevcut token'ı yükle
        current_token = self.token_oku()
        if current_token:
            self.token_entry.insert(0, current_token)
            tk.Label(token_frame,
                    text="✅ Token kaydedilmiş",
                    font=('Arial', 9),
                    bg='#2c3e50', fg='#2ecc71').pack(anchor='w', pady=(5, 0))
        
        # Token kaydet butonu
        self.token_kaydet_btn = tk.Button(token_frame,
                                         text="💾 Token'ı Kaydet",
                                         font=('Arial', 11, 'bold'),
                                         bg='#27ae60', fg='white',
                                         command=self.token_kaydet,
                                         cursor='hand2',
                                         height=2)
        self.token_kaydet_btn.pack(fill='x', pady=(10, 5))
        
        # Ses Ayarları Bölümü
        ses_frame = tk.LabelFrame(main_frame,
                                 text="  🎤 Ses Ayarları  ",
                                 font=('Arial', 11, 'bold'),
                                 bg='#2c3e50', fg='#e74c3c',
                                 padx=20, pady=15)
        ses_frame.pack(fill='x', pady=10)
        
        # Ses kalitesi
        tk.Label(ses_frame,
                text="Ses Kalitesi (Sample Rate):",
                font=('Arial', 10),
                bg='#2c3e50', fg='#ecf0f1').pack(anchor='w', pady=(0, 5))
        
        self.kalite_var = tk.StringVar(value="44100")
        kalite_frame = tk.Frame(ses_frame, bg='#2c3e50')
        kalite_frame.pack(fill='x', pady=(0, 10))
        
        for rate, label in [("22050", "Düşük (22kHz)"), ("44100", "Normal (44kHz)"), ("48000", "Yüksek (48kHz)")]:
            tk.Radiobutton(kalite_frame,
                          text=label,
                          variable=self.kalite_var,
                          value=rate,
                          font=('Arial', 9),
                          bg='#2c3e50', fg='white',
                          selectcolor='#34495e',
                          activebackground='#2c3e50',
                          activeforeground='white').pack(anchor='w')
        
        # Test Bölümü
        test_frame = tk.LabelFrame(main_frame,
                                  text="  🧪 Test  ",
                                  font=('Arial', 11, 'bold'),
                                  bg='#2c3e50', fg='#f39c12',
                                  padx=20, pady=15)
        test_frame.pack(fill='x', pady=10)
        
        tk.Button(test_frame,
                 text="🎤 Mikrofon Testi",
                 font=('Arial', 10, 'bold'),
                 bg='#f39c12', fg='white',
                 command=self.mikrofon_test,
                 cursor='hand2').pack(fill='x', pady=5)
        
        # Butonlar
        buton_frame = tk.Frame(main_frame, bg='#2c3e50')
        buton_frame.pack(pady=(20, 0))
        
        tk.Button(buton_frame,
                 text="Kaydet ve Kapat",
                 font=('Arial', 11, 'bold'),
                 bg='#3498db', fg='white',
                 command=self.kaydet_kapat,
                 cursor='hand2',
                 width=15).pack(side='left', padx=5)
        
        tk.Button(buton_frame,
                 text="İptal",
                 font=('Arial', 11),
                 bg='#95a5a6', fg='white',
                 command=self.pencere.destroy,
                 cursor='hand2',
                 width=15).pack(side='left', padx=5)
        
        # Pencereyi ortala
        self.pencere.transient(parent)
        self.pencere.grab_set()
        self.token_gizli = True
    
    def token_goster_gizle(self):
        """Token'ı göster/gizle"""
        if self.token_gizli:
            self.token_entry.config(show='')
            self.goster_btn.config(text='🙈')
            self.token_gizli = False
        else:
            self.token_entry.config(show='*')
            self.goster_btn.config(text='👁️')
            self.token_gizli = True
    
    def token_oku(self):
        """Kaydedilmiş token'ı oku"""
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
        """Token'ı kaydet ve ngrok'a ekle"""
        token = self.token_entry.get().strip()
        
        if not token:
            messagebox.showwarning("Uyarı", "Lütfen token giriniz!")
            return
        
        try:
            # Config dosyasına kaydet
            config_file = os.path.expanduser("~/.voice_chat_config.json")
            config = {'ngrok_token': token, 'sample_rate': self.kalite_var.get()}
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
            
            # Ngrok'a token'ı ekle
            result = subprocess.run(['ngrok', 'config', 'add-authtoken', token],
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Başarılı", 
                    "✅ Token başarıyla kaydedildi!\n\n"
                    "Artık ngrok sunucusunu başlatabilirsiniz.")
            else:
                messagebox.showerror("Hata", 
                    f"Token kaydedilemedi:\n{result.stderr}\n\n"
                    "Ngrok yüklü mü?")
                
        except FileNotFoundError:
            messagebox.showerror("Ngrok Bulunamadı",
                "Ngrok yüklü değil!\n\n"
                "Kurulum: https://ngrok.com/download")
        except Exception as e:
            messagebox.showerror("Hata", f"Beklenmeyen hata:\n{e}")
    
    def mikrofon_test(self):
        """Mikrofon testi yap"""
        messagebox.showinfo("Mikrofon Testi",
            "🎤 Mikrofon testi başlıyor...\n\n"
            "Konuşun, sesinizi duyabileceksiniz.\n"
            "Pencereyi kapatınca test sonlanır.")
        
        # Test penceresi
        test_win = tk.Toplevel(self.pencere)
        test_win.title("🎤 Mikrofon Test")
        test_win.geometry("300x150")
        test_win.configure(bg='#2c3e50')
        
        tk.Label(test_win,
                text="🎤 Konuşun...",
                font=('Arial', 14, 'bold'),
                bg='#2c3e50', fg='#2ecc71').pack(expand=True)
        
        tk.Button(test_win,
                 text="Testi Durdur",
                 font=('Arial', 11, 'bold'),
                 bg='#e74c3c', fg='white',
                 command=test_win.destroy,
                 cursor='hand2').pack(pady=10)
        
        # Basit echo testi thread'i
        def test_echo():
            try:
                import pyaudio
                audio = pyaudio.PyAudio()
                
                stream_in = audio.open(format=pyaudio.paInt16,
                                      channels=1,
                                      rate=int(self.kalite_var.get()),
                                      input=True,
                                      frames_per_buffer=1024)
                
                stream_out = audio.open(format=pyaudio.paInt16,
                                       channels=1,
                                       rate=int(self.kalite_var.get()),
                                       output=True,
                                       frames_per_buffer=1024)
                
                while test_win.winfo_exists():
                    data = stream_in.read(1024, exception_on_overflow=False)
                    stream_out.write(data)
                
                stream_in.stop_stream()
                stream_in.close()
                stream_out.stop_stream()
                stream_out.close()
                audio.terminate()
            except:
                pass
        
        threading.Thread(target=test_echo, daemon=True).start()
    
    def kaydet_kapat(self):
        """Ayarları kaydet ve kapat"""
        config_file = os.path.expanduser("~/.voice_chat_config.json")
        try:
            config = {'sample_rate': self.kalite_var.get()}
            
            # Mevcut token varsa koru
            token = self.token_entry.get().strip()
            if token:
                config['ngrok_token'] = token
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
            
            messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
            self.pencere.destroy()
        except Exception as e:
            messagebox.showerror("Hata", f"Ayarlar kaydedilemedi:\n{e}")


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
        self.RATE = self.ayarlardan_rate_al()
        
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
    
    def ayarlardan_rate_al(self):
        """Kaydedilmiş ses kalitesini oku"""
        config_file = os.path.expanduser("~/.voice_chat_config.json")
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    return int(config.get('sample_rate', 44100))
        except:
            pass
        return 44100
    
    def pencere_olustur(self):
        """Ana pencereyi oluştur"""
        self.root = tk.Tk()
        self.root.title("🎙️ Sesli Konuşma Uygulaması")
        self.root.geometry("600x750")
        self.root.configure(bg='#2c3e50')
        self.root.resizable(False, False)
        
        # Menü çubuğu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        ayarlar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="⚙️ Ayarlar", menu=ayarlar_menu)
        ayarlar_menu.add_command(label="Ngrok Token", command=self.ayarlar_ac)
        ayarlar_menu.add_command(label="Ses Ayarları", command=self.ayarlar_ac)
        ayarlar_menu.add_separator()
        ayarlar_menu.add_command(label="Çıkış", command=self.kapat)
        
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
        
        # Ayarlar butonu (sağ üstte)
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
                                width=35)
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
                                   width=35)
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
        
        ip_giris_frame.pack(fill='x', pady=5)
        
        tk.Label(ip_giris_frame,
                text="Sunucu Adresi (örnek: 0.tcp.ngrok.io:12345)",
                font=('Arial', 9),
                bg='#2c3e50', fg='#ecf0f1').pack(anchor='w', pady=(0,5))
        
        self.ip_entry = tk.Entry(ip_giris_frame,
                                font=('Courier', 11),
                                bg='#34495e', fg='white',
                                insertbackground='white',
                                relief='flat')
        self.ip_entry.pack(fill='x', ipady=8)

        # Bağlan butonu
        self.baglan_btn = tk.Button(istemci_frame,
                                    text="🔗 Bağlan",
                                    font=('Arial', 12, 'bold'),
                                    bg='#27ae60', fg='white',
                                    cursor='hand2',
                                    height=2,
                                    command=self.baglan)
        self.baglan_btn.pack(fill='x', pady=(10,5))
        
        # Bağlantı durumu
        self.durum_label = tk.Label(istemci_frame,
                                    text="Durum: Bağlı değil ❌",
                                    font=('Arial', 9, 'italic'),
                                    bg='#2c3e50', fg='#e74c3c')
        self.durum_label.pack(pady=(5,0))
        
        # Ses log alanı
        self.log_alani = scrolledtext.ScrolledText(self.root,
                                                  height=10,
                                                  font=('Courier', 10),
                                                  bg='#1a1a1a', fg='#ecf0f1',
                                                  insertbackground='white')
        self.log_alani.pack(fill='both', expand=True, padx=20, pady=15)
        self.log_yaz("Uygulama başlatıldı...")

        # Pencere kapatma işlemi
        self.root.protocol("WM_DELETE_WINDOW", self.kapat)
        self.root.mainloop()
    

    # ---------------- YARDIMCI METOTLAR ---------------- #
    def log_yaz(self, mesaj):
        self.log_alani.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {mesaj}\n")
        self.log_alani.see(tk.END)

    def ayarlar_ac(self):
        AyarlarPenceresi(self.root)

    def kapat(self):
        try:
            if self.baglanti:
                self.baglanti.close()
            if self.client_socket:
                self.client_socket.close()
            if self.server_socket:
                self.server_socket.close()
            if self.ngrok_process:
                self.ngrok_process.terminate()
        except:
            pass
        self.root.destroy()

    # ---------------- SUNUCU ---------------- #
    def ngrok_ile_baslat(self):
        """Ngrok ile sunucu başlat"""
        self.log_yaz("Ngrok ile sunucu başlatılıyor...")
        try:
            # Local sunucu başlat
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', 5000))
            self.server_socket.listen(1)
            self.log_yaz("Yerel sunucu 5000 portunda dinliyor...")

            # Ngrok'u başlat
            self.ngrok_process = subprocess.Popen(['ngrok', 'tcp', '5000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3)

            # Ngrok URL’sini al
            t = requests.get("http://127.0.0.1:4040/api/tunnels").json()
            public_url = t['tunnels'][0]['public_url'].replace("tcp://", "")
            host, port = public_url.split(':')
            self.ngrok_url = (host, port)

            self.log_yaz(f"Ngrok bağlantısı: {host}:{port}")
            BaglantiPenceresi(self.root, host, port)

            threading.Thread(target=self.sunucu_dinle, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu başlatılamadı:\n{e}")
            self.log_yaz(f"Hata: {e}")

    def sunucu_dinle(self):
        """Gelen bağlantıyı kabul et"""
        self.log_yaz("Bağlantı bekleniyor...")
        self.baglanti, addr = self.server_socket.accept()
        self.log_yaz(f"Bağlantı kabul edildi: {addr}")
        self.bagli = True
        self.durum_guncelle(True)
        threading.Thread(target=self.ses_al, daemon=True).start()

    # ---------------- İSTEMCİ ---------------- #
    def baglan(self):
        """İstemci olarak bağlan"""
        adres = self.ip_entry.get().strip()
        if not adres:
            messagebox.showwarning("Uyarı", "Bağlanılacak adresi giriniz!")
            return
        
        try:
            host, port = adres.split(':')
            port = int(port)
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))
            self.log_yaz(f"Sunucuya bağlanıldı: {host}:{port}")
            self.bagli = True
            self.durum_guncelle(True)
            
            threading.Thread(target=self.ses_al, daemon=True).start()
            threading.Thread(target=self.ses_gonder, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Bağlantı Hatası", f"Sunucuya bağlanılamadı:\n{e}")
            self.log_yaz(f"Hata: {e}")

    def durum_guncelle(self, bagli):
        if bagli:
            self.durum_label.config(text="Durum: Bağlı ✅", fg='#2ecc71')
        else:
            self.durum_label.config(text="Durum: Bağlı değil ❌", fg='#e74c3c')

    # ---------------- SES ---------------- #
    def ses_al(self):
        """Karşıdan gelen sesi çal"""
        stream = self.audio.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 output=True,
                                 frames_per_buffer=self.CHUNK)
        soket = self.baglanti or self.client_socket
        while self.bagli:
            try:
                data = soket.recv(self.CHUNK)
                if not data:
                    break
                stream.write(data)
            except:
                break
        stream.stop_stream()
        stream.close()
        self.bagli = False
        self.durum_guncelle(False)
        self.log_yaz("Ses alımı sonlandı.")

    def ses_gonder(self):
        """Mikrofon verisini gönder"""
        stream = self.audio.open(format=self.FORMAT,
                                 channels=self.CHANNELS,
                                 rate=self.RATE,
                                 input=True,
                                 frames_per_buffer=self.CHUNK)
        soket = self.baglanti or self.client_socket
        while self.bagli:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                soket.sendall(data)
            except:
                break
        stream.stop_stream()
        stream.close()
        self.log_yaz("Ses gönderimi sonlandı.")


if __name__ == "__main__":
    SesliKonusmaUygulamasi()
