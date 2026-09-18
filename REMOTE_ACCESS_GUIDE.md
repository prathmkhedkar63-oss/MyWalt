# 🌐 Free Remote Access Guide for MyWalt

You have successfully hosted **MyWalt** locally on your PC (`http://localhost:8000`).
To control your PC files **remotely** from any phone, laptop, or tablet outside your local network for **FREE**, choose one of the recommended methods below.

---

## ⚡ Option 1: Cloudflare Tunnel (`cloudflared`) — RECOMMENDED ⭐⭐⭐⭐⭐

Cloudflare Tunnel is the **best, most secure, and 100% free** method. It gives you an **HTTPS domain** without opening ports on your home router.

### Setup Instructions:
1. **Download Cloudflare CLI**:
   - Download `cloudflared.exe` from [Cloudflare Releases](https://github.com/cloudflare/cloudflared/releases) or install via PowerShell:
     ```powershell
     winget install Cloudflare.cloudflared
     ```
2. **Start the Free Tunnel**:
   - Open PowerShell and run:
     ```powershell
     cloudflared tunnel --url http://localhost:8000
     ```
3. **Access Remotely**:
   - Cloudflare will print a secure HTTPS URL in the console (e.g. `https://random-words.trycloudflare.com`).
   - Open that URL on your phone or remote browser to access your PC files securely with full SSL encryption!

---

## 🔒 Option 2: Tailscale (Private Zero-Trust VPN) — MAXIMUM SECURITY ⭐⭐⭐⭐⭐

Tailscale creates a private, encrypted peer-to-peer network between your PC and your mobile phone / remote laptop. No one else on the internet can even see your server.

### Setup Instructions:
1. **Install Tailscale on your PC**:
   - Download and install Tailscale from [tailscale.com](https://tailscale.com).
   - Log in with Google/Microsoft account.
2. **Install Tailscale on your Phone / Remote Device**:
   - Install the Tailscale app on iOS / Android / Mac / Windows and log in with the same account.
3. **Access Remotely**:
   - Copy your PC's Tailscale IP address (e.g. `100.x.y.z`).
   - On your phone, open `http://100.x.y.z:8000` in your browser.

---

## 🚀 Option 3: ngrok (Instant HTTPS URL) ⭐⭐⭐⭐

ngrok provides an instant secure tunnel link for quick sharing or testing.

### Setup Instructions:
1. **Download ngrok**:
   - Download from [ngrok.com](https://ngrok.com) or install via PowerShell:
     ```powershell
     winget install ngrok.ngrok
     ```
2. **Start Tunnel**:
   - Run:
     ```powershell
     ngrok http 8000
     ```
3. **Access Remotely**:
   - Copy the `https://xxxx.ngrok-free.app` link provided by ngrok.

---

## 🟢 Option 4: LocalTunnel (`npx localtunnel`) ⭐⭐⭐⭐

If you have Node.js installed, LocalTunnel requires zero installation.

### Setup Instructions:
1. Open PowerShell and run:
   ```powershell
   npx localtunnel --port 8000
   ```
2. Open the generated `.loca.lt` URL on your phone/remote device.

---

## 🛡️ Summary of Security Layering

When accessed remotely, **MyWalt** protects your computer with multiple defense layers:
1. **Password Protection**: Requires your Master Password to access any file operation.
2. **Session Token**: Authenticated via HttpOnly, SameSite=Strict cookies.
3. **Path Traversal Shield**: Canonical path validation prevents directory traversal attacks (`../`).
4. **IP Lockout**: 5 failed login attempts lock out the IP address for 15 minutes.
5. **Security Headers**: OWASP security headers enabled on all responses.
