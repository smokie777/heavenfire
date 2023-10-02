import { useEffect, useRef } from 'react';
import { MIC_INPUT_DELAY } from './constants';

let mediaRecorder:MediaRecorder;

export const DeepgramSTT = ({
  lunaAnswerMicInput,
  micInputRef,
  lunaNextActionTimeoutRef,
  isSmokieTalkingRef,
  isLunaBusyRef,
  isLunaRespondingToMic
}:{
  lunaAnswerMicInput: () => void;
  micInputRef: React.RefObject<string[]>;
  lunaNextActionTimeoutRef: React.MutableRefObject<number | NodeJS.Timer>;
  isSmokieTalkingRef: React.MutableRefObject<boolean>;
  isLunaBusyRef: React.RefObject<boolean>;
  isLunaRespondingToMic: boolean;
}) => {
  const deepgramKeepAliveIntervalRef = useRef<number | NodeJS.Timer>();

  useEffect(() => {
    const socket = new WebSocket(
      'wss://api.deepgram.com/v1/listen',
      [ 'token', process.env.REACT_APP_DEEPGRAM_KEY as string ]
    );

    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      mediaRecorder = new MediaRecorder(stream);
      
      socket.onopen = () => {
        mediaRecorder.addEventListener('dataavailable', event => {
          if (event.data.size > 0 && socket.readyState === 1) {
            socket.send(event.data);
          }
        });
        mediaRecorder.start(250);
        mediaRecorder.pause();
        
        deepgramKeepAliveIntervalRef.current = setInterval(() => {
          socket.send(JSON.stringify({ 'type': 'KeepAlive' }));
        }, 11000);

        console.log('Initialized: Deepgram STT Websocket');
      };

      socket.onmessage = (message) => {
        // the ideal behavior is to stop recording mic input when luna is busy
        // however, the microphone hardware picks up a few seconds of audio transcripts at a time.
        // this means that luna will "hear herself speak" towards the end of her speech. it's annoying, but unavoidable.
        // some work-arounds are:
        // 1. wearing headphones
        // 2. disabling audio preview in VTube Studio/Streamlabs
        // 3. adding an artificial cooldown period, where luna cannot take input for x seconds after speaking.
        if (isLunaBusyRef.current) {
          return;
        }

        // the try catch is for if you disable "luna responding to mic"
        try {
          const received = JSON.parse(message.data);
          const transcript = received.channel.alternatives[0].transcript;
          
          if (transcript) {
            if (lunaNextActionTimeoutRef.current) {
              clearTimeout(lunaNextActionTimeoutRef.current);
            }
            isSmokieTalkingRef.current = true;
            if (received.is_final) {
              if (micInputRef.current) {
                micInputRef.current.push(transcript);
              }
              lunaNextActionTimeoutRef.current = setTimeout(() => {
                lunaAnswerMicInput();
              }, MIC_INPUT_DELAY);
            }
          }
        } catch {}
      };

      socket.onclose = () => {
        console.log('Closed: Deepgram STT Websocket');
      };

      socket.onerror = (error) => {
      };
    });

    return () => {
      if (lunaNextActionTimeoutRef.current) {
        clearTimeout(lunaNextActionTimeoutRef.current);
      }
      clearInterval(deepgramKeepAliveIntervalRef.current);
      socket.close(); 
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (mediaRecorder) {
      if (isLunaRespondingToMic) {
        mediaRecorder.resume();
      } else {
        mediaRecorder.pause();
      }
    }
  }, [isLunaRespondingToMic])

  return null;
};
