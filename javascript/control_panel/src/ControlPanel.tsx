import './ControlPanel.scss';
import { useState, useRef, useCallback, useEffect } from 'react';
import { Spacer } from './Spacer';
import { fetch_post } from './fetch_functions';
import { Subtitles } from './Subtitles';
import { DeepgramSTT } from './DeepgramSTT';
import { Helmet } from 'react-helmet';

// make channel point redeem for luna saying "im gonna punch you in the face"

export const ControlPanel = () => {
  const [textBoxInput, setTextBoxInput] = useState('');
  const [prompt, setPrompt] = useState('');
  const [raw, setRaw] = useState('');
  const [edited, setEdited] = useState('');
  const [subtitlesState, setSubtitlesState] = useState<React.ComponentProps<typeof Subtitles>>({
    text: '',
    subtitles: []
  });
  const [isSTTActive, setIsSTTActive] = useState(false);
  const [isTwitchChatReactOn, setIsTwitchChatReactOn] = useState(true);
  const [isQuietModeOn, setIsQuietModeOn] = useState(true);
  const isBusyRef = useRef(false);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:4000');
    ws.addEventListener('open', () => {
      console.log('Connected to WebSocket server!');
    });
    ws.addEventListener('message', (_data) => {
      const data = JSON.parse(_data.data);
      if (data.hasOwnProperty('prompt')) {
        setPrompt(data.prompt);
      }
      if (data.hasOwnProperty('raw')) {
        setRaw(data.raw);
      }
      if (data.hasOwnProperty('edited')) {
        setEdited(data.edited);
      }
      if (data.hasOwnProperty('edited') && data.hasOwnProperty('subtitles')) {
        setSubtitlesState({
          text: data.edited,
          subtitles: data.subtitles
        });
      }
      if (data.hasOwnProperty('is_busy')) {
        setIsBusy(data.is_busy);
      }
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // the deepgram websocket doesn't play well with react state, so we have to use a ref here.
  const setIsBusy = useCallback((i:boolean) => {
    isBusyRef.current = i;
    (document.getElementsByClassName('luna_portrait')[0] as HTMLElement).style.border = (
      i ? '7px solid red' : '7px solid mediumseagreen'
    );
  }, []);

  const answerTextBox = () => {
    setIsBusy(true);
    fetch_post('/receive_prompt', {
      prompt: textBoxInput,
      priority: 'priority_twitch_chat_queue'
    });
    setTextBoxInput('');
  };

  const reactToScreen = () => {
    setIsBusy(true);
    fetch_post('/react_to_screen', {});
  };

  const eraseMemory = () => {
    fetch_post('/erase_memory');
  };

  const cancelSpeech = () => {
    fetch_post('/cancel_speech');
    setSubtitlesState({
      text: '',
      subtitles: []
    });
  };

  const sing = async() => {
    // TODO: implement a dropdown with all possible songs
    const songs = ['edamame', 'ringer', 'newcrack', 'iwantitthatway', 'yesterday'];
    const song = textBoxInput;
    if (!songs.includes(song)) {
      return;
    }
    setTextBoxInput('');
    setIsBusy(true);
    await fetch_post('/sing', {
      song,
    });
    setIsBusy(false);
  };

  const shutDownServer = () => {
    setIsBusy(false);
    fetch_post('/shut_down_server');
  };

  // const lunaReadTextBox = () => {
  //   fetch_post('/receive_prompt', {
  //     prompt: textBoxInput,
  //     priority: PRIORITY_QUEUE_MAP['priority_mic_input']
  //   });
  //   setTextBoxInput('');
  // };

  const toggleIsTwitchChatReactOn = () => {
    const newValue = !isTwitchChatReactOn;
    setIsTwitchChatReactOn(newValue);
    fetch_post('/set_config_variable', {
      name: 'is_twitch_chat_react_on',
      value: newValue
    });
  };

  const toggleIsQuietModeOn = () => {
    const newValue = !isQuietModeOn;
    setIsQuietModeOn(newValue);
    fetch_post('/set_config_variable', {
      name: 'is_quiet_mode_on',
      value: newValue
    });
  };

  return (
    <div className='app_container'>
      <Helmet><title>Heavenfire Control Panel</title></Helmet>

      {isSTTActive && (
        <DeepgramSTT isBusyRef={isBusyRef} setIsBusy={setIsBusy} />
      )}

      <div className='app'>
        <img
          className='luna_portrait'
          alt='luna'
          src='luna_portrait.png'
          width='200px'
          height='200px'
          style={{ border: '7px solid mediumseagreen' }}
        />

        <div className='toggles'>
          <button onClick={() => setIsSTTActive(prevIsSTTActive => !prevIsSTTActive)}>
            Turn {isSTTActive ? 'off' : 'on'} mic
          </button>
          <Spacer height={3} />

          <input
            type='checkbox'
            checked={isTwitchChatReactOn}
            onChange={toggleIsTwitchChatReactOn}
          />
          Reading twitch chat?
          <Spacer height={3} />

          <input
            type='checkbox'
            checked={isQuietModeOn}
            onChange={toggleIsQuietModeOn}
          />
          Quiet mode?
        </div>
        <div className='responses'>
          <p>PROMPT: {prompt}</p>
          <p>RAW: {raw === edited ? '...' : raw}</p>
          <p>EDITED: {edited}</p>
        </div>
        <hr />
        <textarea
          value={textBoxInput}
          onChange={(e) => setTextBoxInput(e.target.value)}
        />
        <Spacer height={10} />
        <div className='textbox_buttons'>
          <button onClick={answerTextBox}>Answer</button>
          <Spacer width={20} />
          <button onClick={reactToScreen}>React to screen</button>
          <Spacer width={20} />
          <button onClick={eraseMemory}>Clear memory</button>
          <Spacer width={20} />
          <button onClick={cancelSpeech}>Cancel speech</button>
          <Spacer width={20} />
          <button onClick={sing}>Sing</button>
          <Spacer width={20} />
          <button onClick={shutDownServer}>Shut down server</button>
          <Spacer width={20} />
          {/* <button onClick={() => lunaReadTextBox(false)}>Read</button>
          <Spacer width={20} />
          <button onClick={() => lunaReadTextBox(true)}>Generate audio file</button>
          <Spacer width={20} /> */}
        </div>
      </div>

      <Subtitles {...subtitlesState} />
    </div>
  );
};
