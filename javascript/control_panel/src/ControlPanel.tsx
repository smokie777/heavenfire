import "./ControlPanel.scss";
import { useState, useEffect, useRef } from "react";
import { Spacer } from "./Spacer";
import { fetch_post } from "./fetch_functions";
import { Subtitles } from "./Subtitles";
import { Helmet } from "react-helmet";
import { PRIORITY_QUEUE_PRIORITIES, WEBSOCKET_EVENT_TYPES } from "./enums";
import { song_subtitles } from "./song_subtitles";
import { songs } from "./songs";

// make channel point redeem for luna saying "im gonna punch you in the face"

export const ControlPanel = () => {
  const wsRef = useRef<WebSocket | null>(null);
  const [textBoxInput, setTextBoxInput] = useState("");
  const [prompt, setPrompt] = useState("");
  const [raw, setRaw] = useState("");
  const [edited, setEdited] = useState("");
  const [subtitlesState, setSubtitlesState] = useState<
    React.ComponentProps<typeof Subtitles>
  >({
    text: "",
    subtitles: [],
  });
  const [isTwitchChatReactOn, setIsTwitchChatReactOn] = useState(true);
  const [isQuietModeOn, setIsQuietModeOn] = useState(true);
  const [isBusy, setIsBusy] = useState(false);
  const [areLiveAnimatedEmotesOn, setAreLiveAnimatedEmotesOn] = useState(true);
  const [isDVDActive, setIsDVDActive] = useState(false);
  const [isSpeakingFast, setIsSpeakingFast] = useState(false);

  useEffect(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    const ws = new WebSocket("ws://localhost:4000");
    wsRef.current = ws;
    ws.addEventListener("open", () => {
      console.log("Connected to WebSocket server!");
    });
    ws.addEventListener("message", (_data) => {
      const data = JSON.parse(_data.data);
      if (data.hasOwnProperty("prompt")) {
        setPrompt(data.prompt);
      }
      if (data.hasOwnProperty("raw")) {
        setRaw(data.raw);
      }
      if (data.hasOwnProperty("edited")) {
        setEdited(data.edited);
      }
      if (data.hasOwnProperty("edited") && data.hasOwnProperty("subtitles")) {
        setSubtitlesState({
          text: data.edited,
          subtitles: data.subtitles,
        });
      }
      if (data.hasOwnProperty("is_busy")) {
        setIsBusy(data.is_busy);
      }
    });

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const answerTextBox = () => {
    if (textBoxInput) {
      setIsBusy(true);
      fetch_post("/receive_prompt", {
        prompt: textBoxInput,
        priority: PRIORITY_QUEUE_PRIORITIES.PRIORITY_MIC_INPUT,
      });
      setTextBoxInput("");
    }
  };

  const lunaReadTextBox = () => {
    if (textBoxInput) {
      fetch_post("/speak_text", {
        text: textBoxInput,
        priority: PRIORITY_QUEUE_PRIORITIES.PRIORITY_MIC_INPUT,
      });
      setTextBoxInput("");
    }
  };

  const setContext = () => {
    if (textBoxInput) {
      fetch_post("/set_context", {
        context: textBoxInput,
      });
      setTextBoxInput("");
    }
  };

  const reactToScreen = () => {
    setIsBusy(true);
    fetch_post("/react_to_screen", {});
  };

  const eraseMemory = () => {
    fetch_post("/erase_memory");
  };

  const cancelSpeech = () => {
    fetch_post("/cancel_speech");
    setSubtitlesState({
      text: "",
      subtitles: [],
    });
    fetch_post("/speak_text", {
      text: "this speech has been cancelled by smokie_777.",
      priority: PRIORITY_QUEUE_PRIORITIES.PRIORITY_MIC_INPUT,
    });
  };

  const sing = async () => {
    // TODO: implement a dropdown with all possible songs
    const song = textBoxInput;
    if (!songs.includes(song)) {
      alert(`error: cannot find song ${song}!`);
      return;
    }
    setTextBoxInput("");
    setIsBusy(true);
    if (song_subtitles.hasOwnProperty(song)) {
      setSubtitlesState(song_subtitles[song]);
    }
    await fetch_post("/sing", {
      song,
    });
    setIsBusy(false);
  };

  const getDbRowsByPage = async () => {
    if (textBoxInput) {
      const rows = await fetch_post("/get_db_rows_by_page", {
        model: textBoxInput,
        page: 1,
      });
      console.log(rows);
      setTextBoxInput("");
    }
  };

  const shutDownServer = () => {
    setIsBusy(false);
    fetch_post("/shut_down_server");
  };

  const toggleIsTwitchChatReactOn = () => {
    const newValue = !isTwitchChatReactOn;
    setIsTwitchChatReactOn(newValue);
    fetch_post("/set_backend_state_variable", {
      name: "is_twitch_chat_react_on",
      value: newValue,
    });
  };

  const toggleIsQuietModeOn = () => {
    const newValue = !isQuietModeOn;
    setIsQuietModeOn(newValue);
    fetch_post("/set_backend_state_variable", {
      name: "is_quiet_mode_on",
      value: newValue,
    });
  };

  const toggleEmoteAnimations = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: WEBSOCKET_EVENT_TYPES["TOGGLE_LIVE_ANIMATED_EMOTES"],
        })
      );
      setAreLiveAnimatedEmotesOn((prevState) => !prevState);
    } else {
      alert("WebSocket ded");
    }
  };

  const toggleDVD = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: WEBSOCKET_EVENT_TYPES["TOGGLE_DVD"],
          payload: !isDVDActive,
        })
      );
      setIsDVDActive((prevState) => !prevState);
    } else {
      alert("WebSocket ded");
    }
  };

  const toggleIsSpeakingFast = () => {
    setIsSpeakingFast((prevState) => !prevState);
    fetch_post("/toggle_is_speaking_fast");
  };

  const sendTestToast = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: WEBSOCKET_EVENT_TYPES["SET_TOAST"],
          payload: "test toast!!!!",
        })
      );
    } else {
      alert("WebSocket ded");
    }
  };

  const generateAudioFile = () => {
    if (textBoxInput) {
      setIsBusy(true);
      fetch_post("/generate_audio_file", {
        prompt: textBoxInput,
      });
      setTextBoxInput("");
    }
  };

  const printRaffleEntries = async () => {
    const { entries } = await fetch_post("/print_raffle_entries");
    console.log(entries.join(","));
  };

  return (
    <div className="app_container">
      <Helmet>
        <title>Heavenfire Control Panel</title>
      </Helmet>

      <div className="app">
        <img
          className="luna_portrait"
          alt="luna"
          src="luna_portrait.png"
          width="200px"
          height="200px"
          style={{
            border: isBusy ? "7px solid red" : "7px solid mediumseagreen",
          }}
        />

        <div className="toggles">
          <input
            type="checkbox"
            checked={isTwitchChatReactOn}
            onChange={toggleIsTwitchChatReactOn}
          />
          Reading twitch chat?
          <Spacer height={3} />
          <input
            type="checkbox"
            checked={isQuietModeOn}
            onChange={toggleIsQuietModeOn}
          />
          Quiet mode?
        </div>
        <div className="responses">
          <p>PROMPT: {prompt}</p>
          <p>RAW: {raw === edited ? "..." : raw}</p>
          <p>EDITED: {edited}</p>
        </div>
        <hr />
        <textarea
          value={textBoxInput}
          onChange={(e) => setTextBoxInput(e.target.value)}
        />
        <Spacer height={10} />
        <div className="textbox_buttons">
          <div>
            <button onClick={answerTextBox}>Answer</button>
            <Spacer width={20} />
            <button onClick={lunaReadTextBox}>Read</button>
            <Spacer width={20} />
            <button onClick={reactToScreen}>React to screen</button>
            <Spacer width={20} />
            <button onClick={eraseMemory}>Clear memory</button>
            <Spacer width={20} />
            <button onClick={cancelSpeech}>Cancel speech</button>
            <Spacer width={20} />
            <button onClick={sing}>Sing</button>
            <Spacer width={20} />
            <button onClick={setContext}>Set context</button>
            <Spacer width={20} />
            <button onClick={toggleIsSpeakingFast}>
              Toggle speaking speed: {isSpeakingFast ? 2 : 1}
            </button>
          </div>
          <div>
            <button onClick={toggleEmoteAnimations}>
              Toggle emote animations {areLiveAnimatedEmotesOn ? "off" : "on"}
            </button>
            <Spacer width={20} />
            <button onClick={toggleDVD}>
              Toggle DVD {isDVDActive ? "off" : "on"}
            </button>
            <Spacer width={20} />
            <button onClick={sendTestToast}>Send test toast</button>
            <Spacer width={20} />
            <button onClick={printRaffleEntries}>Print raffle entries</button>
            <Spacer width={20} />
          </div>
          <div>
            <button onClick={generateAudioFile}>Generate audio file</button>
            <Spacer width={20} />
            <button onClick={getDbRowsByPage}>Get DB Rows By Page</button>
            <Spacer width={20} />
            <button onClick={shutDownServer}>Shut down server</button>
            <Spacer width={20} />
          </div>
        </div>
      </div>

      <Subtitles {...subtitlesState} />
    </div>
  );
};
