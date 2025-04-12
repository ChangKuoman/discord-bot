# Foca Bot

Foca Bot is a discord bot primarily for music.

## Info

foca-bot's _audio_ does not work using Skyline's internet due of firewall issues.

## Installation

```bash
npm install ffmpeg-static
```

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Linux:
```bash
export PATH="$PWD/node_modules/ffmpeg-static:$PATH"
python main.py
```

Windows:
```bash
venv\Scripts\activate
$env:PATH = "$PWD\node_modules\ffmpeg-static;$env:PATH"
python main.py
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
