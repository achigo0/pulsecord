# 🔊 PulseCord

**PulseCord** is a real-time peer-to-peer voice communication app built in **Python**.  
Unlike traditional platforms, PulseCord lets you **host your own private voice server** instantly — no third parties, no data collection, no compromises.  
<p align="center">
  <img src="images/BANNER.jpg" alt="Preview" width="100%">
</p>
---

## 🚀 Features

- 🧠 **Self-hosted voice rooms** using `ngrok` tunnels  
- 🔒 **Secure by design** — no external servers or data storage  
- 🎙️ **Low-latency, real-time** voice streaming  
- 💻 **Cross-platform** (Windows, macOS, Linux)  
- 🪶 **Lightweight GUI** built with `Tkinter`  
- ⚙️ **Customizable network settings** (manual port & baud rate control)

---

## 🧩 How It Works

1. One user launches **PulseCord** in *server mode*, generating a unique address via **ngrok**.  
2. That address is shared with the other participant(s).  
3. Others connect using the address and start talking in real time.  
4. Once the app is closed, the connection disappears — no traces left.


Make sure your ngrok token is configured:
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```
---

## ⚙️ Installation

### Prerequisites
- Python 3.10 or newer  
- A working **microphone** and **speaker/headset**  
- `ngrok` account and auth token  

### Clone & Setup

```bash
git clone https://github.com/achigo0/pulsecord.git
cd pulsecord
pip install -r requirements.txt
