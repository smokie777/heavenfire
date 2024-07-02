# heavenfire
Hi, everyone! This is the monorepo codebase for my AI VTuber project. 

# about
I've been working on this on & off since June 2023. I've set the repo to private for a long while, because I was actually streaming with it and didn't want to reveal all of how it worked. But, recently I've decided to make this repo public, as the AI VTuber hype seems to be dying down a bit, and I want to show off what I've built. And, who knows, maybe someone will be inspired by this project, or learn something from it.

Note that you won't be able to actually run this project if you clone it - there are way too many external application dependencies and complications, and also I have gitignored several sensitive files, such as environment files, prompt files, and training datasets. In addition, Luna's LLM is a fine-tuned model linked to my OpenAI account. This is because I built this project as something I can run from my own unique PC setup, not to distribute this as software - if you want to run your own AI VTuber, I recommend you build your own from the ground up, or use something like w_AI_fu which is designed for you to use. 

Luna<br />
<img src="./readme_assets/image.png" alt="luna" width="350" />

Heavenfire<br />
<img src="./readme_assets/image-1.png" alt="heavenfire" width="350" />
<br />

The repo is called heavenfire because it was originally meant for a new AI VTuber I was making called Heavenfire Phyllis. But, due to difficulties in finding a good enough TTS for her, I have postponed the project indefinitely. Currently, I'm just running Luna out of this repo.

# demo
https://github.com/smokie777/heavenfire/assets/31945139/f2281aeb-c332-4695-9ffe-c80fc1346d6f

# ai vtuber features
- read & respond to twitch chat, with short term memory and some long term memory
- acknowledge new twitch subscribers, bit donos, etc.
- listen to and respond to my voice
- sing
- react to screen/pictures/videos
- play scrabble
- chat to people in discord using a discord bot, using text and/or voice

# technical features/technologies used
- **TypeScript frontend:**
  - **Control Panel** in React
  - **Subtitle view** in React
  - **Scrabble integration** based on https://github.com/smokie777/react-scrabble
  - **Stream overlay/animation layer** views in React
  - **Styling** via SCSS
- **JavaScript "middle-end":**
  - **WebSocket server** used to relay information from backend to frontend
- **Python backend:**
  - **Flask REST server** to serve as the centralized entry point for all incoming requests
  - **Priority Queue** system to handle different types of prompts & other actions
  - **LLM integration**
    - Luna uses a fine-tuned GPT-3.5 model
    - I built the fine-tuning dataset myself, by hand-writing 1000 rows of question-answer pairs. The fine-tuned model does a remarkable job of generating responses in the same tone & personality as the training dataset.
    - 1000 tokens of messages can be stored at once in her short term memory (I can increase or decrease this, depending on how much money I want to spend. Note that Luna's system prompt itself is ~300 tokens.)
    - Scripts to generate datasets in .jsonl format for fine-tuning GPT-3.5
  - **SQLAlchemy database layer** (with Marshmallow deserialization library for schemas)
    - Used to store messages for persistence across restarts/different streams
    - Also used to store random statistical/analytic data (that I will probably never query ever)
  - **TTS integration**
    - Luna uses Microsoft Azure.
    - The main flow involves making API requests to get the TTS sound file and subtitles, playing the sound file through VBCable, and sending the subtitles to the React Subtitle view via websocket.
    - There's also an ElevenLabs integration, although it's currently only being used for a channel point redemption, which is a TTS based on my voice 😒
  - **STT integration**
    - The current STT integration uses Microsoft Azure real-time STT. I press a button, and then I can speak to the AI.
    - I was also previously using a Deepgram API integration for STT, but discontinued it (and deleted the code for it) once I realized Azure was much much better and easier to use, for my use case.
  - **Image recognition integration** (for screen/picture/video react)
    - Uses the Microsoft Azure Dense Captioning service to generate image descriptions, which are then sent to the LLM.
  - **Twitch integration using PyTwitchAPI**
    - Uses PubSub, Chat, and Twitch API's for reading twitch chat, new subs/bits/channel point redemptions, !commands, timeout/ban functionality, etc.
  - **Discord bot**
    - Allows users in my discord server to chat with the AI VTuber via text, or voice (yep, the bot can listen to your speech, transcribe it, generate a response, and then speak the response back through the voice channel!)
    - This discord bot can also make requests to the Flask server, which can theoretically allow for potential collab partners to speak to the vtuber in vc, and have the vtuber actually speak the response aloud on stream. (I haven't actually tested this out, though.)
  - **Testing**
    - Unit testing via python's unittest module
  - **VTube Studio integration**
    - I never really managed to implement this, because I was frustrated by VTS's authentication system.
    - For now, the integration is simply using python to trigger hotkeys that trigger VTS actions 🙈
  - **Singing functionality**
    - The song creation pipeline actually exists outside of this repo. It uses a custom RVC model trained off of samples of Luna's voice, and programs like Ultimate Vocal Remover and Audacity to generate the song files. I haven't invested too much time into this aspect of the project, so the quality of her singing is only mediocre for now

Here is a really outdated diagram of how everything comes together in terms of system design:

<img src="./readme_assets/heavenfire_system_design.png" alt="heavenfire system design" width="1000" />

# costs
This project is not free, and can get expensive if I don't pay enough attention to cutting costs as much as possible. Here are some rough estimates of monthly costs:
- OpenAI: \$20 subscription, \$10-20 usage
- Azure: \$10-20 usage
- ElevenLabs: \$5 subscription
- Total: \$45-65 monthly
- In addition, every time I run Luna's GPT-3.5 fine-tuning job using my dataset of 1000 rows, I have to pay ~$12. However, I've only ever run this job a few times, and don't really plan on running it again, as I am pretty happy with the performance of her current fine-tuned model.

# bootstrapping instructions
First, install Node.js (v19.7.0) and Python (3.10.10).

/javascript/websocket
1. npm i
2. node index.js

/javascript/control_panel
1. npm i
2. npm start

/javascript/react-scrabble-integration
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
9. Ensure Firefox is set up to render all background windows/tabs, so that streamlabs can pick up all the necessary views
10. Start app: python3 server.py
11. (extra) start discord bot: python3 luna_discord_bot.py (may need to navigate to Applications/python and run the install certificates script)

# running instructions
1. Open OBS and start virtual camera for the vtuber's idle animation
2. Open VTube studio, and enable "preview speech"
3. Open windows media player (for eleven labs tts)
4. Open 3 windows of firefox for control panel/overlay/animation layer:
  - http://localhost:3001
  - http://localhost:3001/overlay or http://localhost:3001/overlaywithtimer for stream countdown
  - http://localhost:3001/animations
5. Open Spotify and play some music
6. Open twitch chat popout and place over control panel, so I can actually read chat
7. Open streamlabs, and start streaming!

# misc image gallery
Control panel!<br />
<img src="./readme_assets/image-2.png" alt="control panel" width="500" />

Discord bot!<br />
<img src="./readme_assets/image-5.png" alt="discord bot" width="500" />

Stream overlay!<br />
<img src="./readme_assets/image-3.png" alt="luna" width="500" />

Animation layer!<br />
<img src="./readme_assets/image-4.png" alt="luna" width="500" />
