# Ferramentas Fé & Razão

- transcrever.py: faster-whisper medium, lê audio.wav (16 kHz mono) e gera words.json (palavras com tempo).
- make_cortes.py: renderiza os cortes 1080x1920 no padrão Fé & Razão.
  Uso (na pasta de trabalho): SRC=video.mp4 WORDS=words.json CUTS=cuts.json CROPX=558 python3 make_cortes.py [ids]
  CROPX = posição X do recorte 864x1080 (use o centro do rosto menos 432). Saída em out2/.
- exemplo_cuts.json: formato do cuts.json (id, s, e em segundos, title com [[palavra]] em dourado).
Requer: ffmpeg, rsvg-convert, Pillow, fontes Crimson Text e Poppins.
