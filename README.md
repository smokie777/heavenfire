# heavenfire
Codebase for Heavenfire Phyllis the AI VTuber

# bootstrapping instructions
First, you'll need to install Node.js (v19.7.0) and Python (3.10.10).

/javascript/websocket
1. npm i
2. node index.js

/javascript/control_panel
1. npm i
2. npm start

/python
1. Install pip: https://pip.pypa.io/en/stable/installation/
2. Create venv: python3 -m venv .venv
3. Activate venv: source .venv/bin/activate
4. Confirm python is set up properly:
which python
python -V
5. Install portaudio (required to install pyaudio): brew install portaudio
6. Install packages: pip install -r requirements.txt (if this fails on the PyAudio step, may need to install or update XCode)
7. Install ffmpeg for the TTS to work: brew install ffmpeg (verify it works by running: ffmpeg)
8. Make sure the audio is piped through the correct output (check get_pyaudio_output_audio_index())
9. Start app: python3 server.py
10. (extra) start discord bot: python3 luna_discord_bot.py (may need to navigate to Applications/python and run the install certificates script)=
