---
name: vo-humanizer-indonesian
description: Generate VO Indonesia santai via VoiceStudio Docker container
license: MIT
metadata:
  version: "1.0.0"
---

# VO Humanizer Indonesian

Generate VoiceOver Indonesia casual/friendly via VoiceStudio Docker (port 3900).

## Setup

Container: `ghcr.io/debpalash/voicestudio:0.5.6`, API key dari env `OMNIVOICE_API_KEY`.

## API Call

```python
import requests
K = '<OMNIVOICE_API_KEY>'
H = {'Authorization': 'Bearer ' + K}
r = requests.post('http://127.0.0.1:3900/v1/audio/speech', headers=H,
    json={
        'model': 'omnivoice',
        'voice': 'nova',  # atau 'alloy' (wanita), 'echo' (pria)
        'input': '<TEKS>',
        'instructions': 'speak in casual, friendly, relaxed Indonesian. Natural conversational tone like explaining to a friend. Comfortable pace, warm and approachable.',
        'language': 'id',
        'speed': 1.1,  # 1.0 = normal, 1.1 = 10% lebih cepat
        'response_format': 'mp3'
    }, timeout=120)
open('output.mp3', 'wb').write(r.content)
```

## Humanizer Rules

Naskah harus:
- Sapaan pembuka: "Halo!", "Jadi gini", "Oke"
- Kata penghubung santai: "terus", "karena", "tapi", "nah"
- Hindari kaku: "Silakan lakukan", "Harap perhatikan"
- Panggil penonton: "kamu", "kalian"
- Akhiran: "ya", "kok", "dong"

## Voices

- `nova` — wanita, hangat, tutorial
- `alloy` — pria, netral, dokumentasi
- `echo` — pria, santai, vlog
- `shimmer` — wanita, lembut, storytelling

## Speed

- 0.9-1.0: lambat, penekanan
- 1.0-1.1: normal, santai
- 1.1-1.2: cepat, tutorial padat
- 1.2-1.4: sangat cepat, highlight

## Output Duration Check

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 output.mp3
```
