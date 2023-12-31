import { useEffect, useRef } from 'react';
import { fetch_post } from './fetch_functions';
import { PRIORITY_QUEUE_PRIORITIES } from './enums';

const MIC_INPUT_DELAY = 1500;

let mediaRecorder:MediaRecorder;

export const DeepgramSTT = ({
  isBusyRef,
  setIsBusy
}:{
  isBusyRef: React.MutableRefObject<boolean>;
  setIsBusy: (i: boolean) => void;
}) => {
  const deepgramKeepAliveIntervalRef = useRef<number | NodeJS.Timer>();
  const micInputRef = useRef<string[]>([]);
  const sendSpeechTimeoutRef = useRef<number | NodeJS.Timer>();

  const socketOnMessage = (message:MessageEvent) => {
    if (isBusyRef.current) {
      return;
    }

    const received = JSON.parse(message.data);
    const transcript = received.channel.alternatives[0].transcript;
    
    if (transcript) {
      clearTimeout(sendSpeechTimeoutRef.current);
      if (received.is_final) {
        micInputRef.current.push(transcript);
        sendSpeechTimeoutRef.current = setTimeout(() => {
          const cleanedMicInput = micInputRef.current
            .join(' ')
            .split(' ')
            .map(i => ['lin', 'lena', 'linda', 'elena', 'lana'].includes(i) ? 'luna' : i)
            .map(i => ['smoky', 'smokey'].includes(i) ? 'smokie' : i)
            .join(' ');
          setIsBusy(true);
          fetch_post('/receive_prompt', {
            prompt: `Smokie: ${cleanedMicInput}`,
            // prompt: `(paraphrase and repeat): ${cleanedMicInput}`,
            priority: PRIORITY_QUEUE_PRIORITIES.PRIORITY_MIC_INPUT
          });
          micInputRef.current = [];
        }, MIC_INPUT_DELAY);
      }
    }
  };

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
        
        deepgramKeepAliveIntervalRef.current = setInterval(() => {
          socket.send(JSON.stringify({ 'type': 'KeepAlive' }));
        }, 11000);

        console.log('Initialized: Deepgram STT Websocket');
      };

      socket.onmessage = socketOnMessage;

      socket.onclose = () => {
        console.log('Closed: Deepgram STT Websocket');
      };

      socket.onerror = (error) => {
      };
    });

    return () => {
      clearTimeout(sendSpeechTimeoutRef.current);
      clearInterval(deepgramKeepAliveIntervalRef.current);
      socket.close(); 
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return null;
};
