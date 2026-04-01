# 🎥 Mini-Zoom — Projekt P2P WebRTC

**Przedmiot:** Strumieniowanie Audio-Video  
**Technologie:** Node.js · Express · Socket.io · WebRTC · Tailwind CSS

---

## 📦 Instalacja i uruchomienie

```bash
# 1. Zainstaluj zależności (jednorazowo)
npm install

# 2. Uruchom serwer
npm start
```

Serwer wypisze w konsoli adres HTTPS, np.:
```
https://192.168.1.42:3000
```

---

## 🌐 Jak testować w sieci LAN (Wi-Fi)

1. Upewnij się, że oba urządzenia są w **tej samej sieci Wi-Fi**
2. Na **Urządzeniu A** i **Urządzeniu B** otwórz adres `https://192.168.x.x:3000`
3. Kliknij **"Zaawansowane" → "Przejdź mimo to"** (certyfikat self-signed)
4. Na obu urządzeniach wpisz **to samo ID pokoju** (np. `test-123`)
5. Kliknij "Dołącz do rozmowy" – połączenie P2P zostanie nawiązane automatycznie

---

## 🏗️ Struktura projektu

```
mini-zoom/
├── server.js          ← Serwer sygnalizacyjny (Node.js + HTTPS + Socket.io)
├── public/
│   ├── index.html     ← Interfejs użytkownika (Tailwind CSS dark mode)
│   └── client.js      ← Logika WebRTC (RTCPeerConnection, SDP, ICE)
├── package.json
└── README.md
```

---

## 🔬 Teoria — Jak działa WebRTC P2P?

### 1. Sygnalizacja (przez serwer Socket.io)

WebRTC wymaga wstępnej wymiany metadanych:

| Etap | Co jest wysyłane | Cel |
|------|------------------|-----|
| **SDP Offer** | Parametry mediów inicjatora | "Oto co mogę wysyłać" |
| **SDP Answer** | Parametry mediów odbiorcy | "OK, akceptuję i oto moje" |
| **ICE Candidates** | Adresy IP i porty | "Tędy możesz mnie dosięgnąć" |

### 2. SDP (Session Description Protocol)

Tekstowy dokument opisujący:
- Dostępne kodeki wideo: **VP8, VP9, H.264, AV1**
- Dostępne kodeki audio: **Opus** (48kHz, stereo)
- Kierunek transmisji: `sendrecv`
- Fingerprinty certyfikatów DTLS (szyfrowanie)

### 3. ICE (Interactive Connectivity Establishment)

Hierarchia kandydatów (od najlepszego):
1. **host** — bezpośredni IP LAN (`192.168.x.x`) ← **używany w Wi-Fi**
2. **srflx** — IP odkryty przez STUN Google (NAT traversal)
3. **relay** — TURN server (nie używamy — wymaga kosztów)

### 4. Szyfrowanie (obowiązkowe w WebRTC)

- **DTLS** (Datagram TLS) — szyfrowanie warstwy transportu
- **SRTP** (Secure RTP) — szyfrowanie strumieni audio/video
- Szyfrowanie jest **obowiązkowe** w WebRTC — nie można go wyłączyć!

### 5. Kodeki i kompresja

```
Kamera → MediaStream → RTCPeerConnection
                          ↓ (enkodowanie)
                       VP8/H.264 (wideo) + Opus (audio)
                          ↓ (pakietyzacja)
                       RTP/SRTP pakiety
                          ↓ (transmisja P2P przez UDP)
                       RTCPeerConnection (zdalny)
                          ↓ (dekodowanie)
                       <video> element
```

---

## 📡 Dlaczego HTTPS jest wymagane?

Przeglądarka udostępnia `navigator.mediaDevices.getUserMedia()` **tylko w Secure Context**:
- `https://` — każdy host
- `http://localhost` — tylko lokalnie

Używamy certyfikatu **self-signed** generowanego przez bibliotekę `pem` (OpenSSL).

---

## 🛠️ Technologie (wszystkie darmowe/open-source)

| Technologia | Wersja | Cel |
|-------------|--------|-----|
| Node.js | LTS | Środowisko uruchomieniowe |
| Express | 4.x | Serwer HTTP/HTTPS |
| Socket.io | 4.x | Sygnalizacja WebRTC + czat |
| pem | 1.x | Generowanie certyfikatów SSL |
| WebRTC API | natywne | Streaming P2P (wbudowane w przeglądarkę) |
| Tailwind CSS | CDN | Stylowanie interfejsu |
| Syne + JetBrains Mono | Google Fonts | Typografia |
| STUN Google | darmowy | Wykrywanie publicznego IP |
