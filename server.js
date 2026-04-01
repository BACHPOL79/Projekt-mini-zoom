'use strict';

const https   = require('https');
const os      = require('os');
const path    = require('path');
const forge   = require('node-forge');
const express = require('express');
const { Server } = require('socket.io');

const PORT = 3000;
const app  = express();
app.use(express.static(path.join(__dirname, 'public')));

function getLocalIP() {
  for (const ifaces of Object.values(os.networkInterfaces())) {
    for (const i of ifaces) {
      if (i.family === 'IPv4' && !i.internal) return i.address;
    }
  }
  return '127.0.0.1';
}

function makeCert(ip) {
  const keys = forge.pki.rsa.generateKeyPair(2048);
  const cert = forge.pki.createCertificate();
  cert.publicKey    = keys.publicKey;
  cert.serialNumber = Date.now().toString(16);
  cert.validity.notBefore = new Date();
  cert.validity.notAfter  = new Date(Date.now() + 365 * 86400000);
  const attrs = [{ name: 'commonName', value: ip }];
  cert.setSubject(attrs);
  cert.setIssuer(attrs);
  cert.setExtensions([
    { name: 'basicConstraints', cA: false },
    { name: 'keyUsage', digitalSignature: true, keyEncipherment: true },
    { name: 'extKeyUsage', serverAuth: true },
    { name: 'subjectAltName', altNames: [
      { type: 7, ip },
      { type: 7, ip: '127.0.0.1' },
      { type: 2, value: 'localhost' },
    ]},
  ]);
  cert.sign(keys.privateKey, forge.md.sha256.create());
  return {
    key:  forge.pki.privateKeyToPem(keys.privateKey),
    cert: forge.pki.certificateToPem(cert),
  };
}

const localIP = getLocalIP();
console.log('🔐 Generuję certyfikat…');
const tls = makeCert(localIP);
console.log('✅ Certyfikat gotowy\n');

const server = https.createServer({ key: tls.key, cert: tls.cert, minVersion: 'TLSv1.2' }, app);
const io     = new Server(server, { cors: { origin: '*' } });

// pokoje: Map<roomId, [socketId1, socketId2]>
const rooms = new Map();

io.on('connection', socket => {
  console.log(`[+] ${socket.id.slice(0,6)} połączył się`);

  socket.on('join-room', ({ roomId, username }) => {
    if (!rooms.has(roomId)) rooms.set(roomId, []);
    const room = rooms.get(roomId);

    if (room.length >= 2) {
      socket.emit('room-full');
      return;
    }

    room.push({ id: socket.id, username });
    socket.join(roomId);
    socket.data = { roomId, username };

    const jestPierwszy = room.length === 1;

    // powiadom klienta czy jest pierwszy czy drugi
    socket.emit('room-joined', {
      roomId,
      jestInitiatorem: !jestPierwszy,   // DRUGI wysyła Offer
      peerUsername: jestPierwszy ? null : room[0].username,
    });

    if (!jestPierwszy) {
      // powiadom pierwszego że ktoś dołączył
      socket.to(roomId).emit('peer-joined', { username });
    }

    console.log(`[*] ${socket.id.slice(0,6)} → #${roomId} (${room.length}/2)`);
  });

  // serwer przekazuje SDP i ICE w obie strony — nie modyfikuje, tylko routuje
  socket.on('offer',         ({ roomId, sdp })       => { console.log('→ offer');     socket.to(roomId).emit('offer',         { sdp }); });
  socket.on('answer',        ({ roomId, sdp })       => { console.log('→ answer');    socket.to(roomId).emit('answer',        { sdp }); });
  socket.on('ice-candidate', ({ roomId, candidate }) => {                              socket.to(roomId).emit('ice-candidate', { candidate }); });

  socket.on('mic-status', ({ roomId, muted }) => {
    socket.to(roomId).emit('peer-mic-status', { muted });
  });

  socket.on('chat-message', ({ roomId, message, username }) => {
    io.to(roomId).emit('chat-message', {
      from: socket.id, username, message,
      time: new Date().toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit' }),
    });
  });

  socket.on('disconnect', () => {
    const { roomId } = socket.data || {};
    if (!roomId || !rooms.has(roomId)) return;
    const room = rooms.get(roomId).filter(p => p.id !== socket.id);
    if (room.length === 0) rooms.delete(roomId);
    else {
      rooms.set(roomId, room);
      socket.to(roomId).emit('peer-disconnected');
    }
    console.log(`[-] ${socket.id.slice(0,6)} opuścił #${roomId}`);
  });
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('╔═══════════════════════════════════════════╗');
  console.log('║           🎥  MINI-ZOOM  🎥               ║');
  console.log('╠═══════════════════════════════════════════╣');
  console.log(`║  Lokalnie:  https://localhost:${PORT}        ║`);
  console.log(`║  Sieć LAN:  https://${localIP}:${PORT}    ║`);
  console.log('╠═══════════════════════════════════════════╣');
  console.log('║       Zaawansowane → Przejdź mimo to      ║');
  console.log('╚═══════════════════════════════════════════╝\n');
});