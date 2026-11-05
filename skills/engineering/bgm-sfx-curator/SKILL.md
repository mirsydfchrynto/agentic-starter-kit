---
name: bgm-sfx-curator
description: Download background music & SFX bebas royalti
license: MIT
metadata:
  version: "1.0.0"
---

# BGM & SFX Curator

Download background music dan sound effects bebas royalti.

## Music Sources (No Signup, Direct Download)

### 1. Incompetech (Kevin MacLeod) — CC-BY

Direct MP3: `https://incompetech.com/music/royalty-free/mp3-royaltyfree/<TRACK>.mp3`

Contoh tracks:
- `Carefree` — ceria, ringan, tutorial
- `Wholesome` — hangat, positif
- `Cipher` — tech, electronic, modern
- `Electrodoodle` — playful, upbeat
- `Life of Riley` — bouncy, fun
- `Rollin at 5` — smooth, jazzy

Attribution: "Music: Kevin MacLeod (incompetech.com), Licensed under Creative Commons: By Attribution 4.0"

### 2. Pixabay Music (search-based, no direct URL pattern)

Cari manual: `https://pixabay.com/music/search/<query>/`
Download via browser, simpan ke `/tmp/assets/`

### 3. Free Music Archive (FMA)

API: `https://freemusicarchive.org/search?quicksearch=<query>&song_filter=CC0`

## SFX Sources

### 1. Pixabay SFX

`https://pixabay.com/sound-effects/search/<query>/`

Contoh query:
- `ui click`, `button click`, `notification`
- `pop`, `ding`, `success`
- `transition whoosh`, `swoosh`

### 2. Freesound (CC0)

`https://freesound.org/search/?q=<query>&f=license:%22Creative+Commons+0%22`

## Download Strategy

```bash
# Incompetech
curl -sL -o track.mp3 "https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3"

# For Pixabay/FMA: use browser automation atau manual download
```

## Mixing Levels (Video)

- Background music: -18 dB to -24 dB (di bawah VO)
- VO: -12 dB to -16 dB (jelas, dominant)
- SFX: -10 dB to -14 dB (punchy, sesaat)
- Ducking: sidechaincompress threshold=0.02 ratio=8 attack=10 release=300

## Tempo Matching

Musik harus match video tempo:
- Video cepat (60s): 100-120 BPM
- Video normal (90-120s): 80-100 BPM
- Video lambat (>120s): 60-80 BPM
