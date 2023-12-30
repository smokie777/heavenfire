import './Animations.scss';
import { Helmet } from 'react-helmet';
import { useEffect, useState, useRef } from 'react';
import { Spacer } from './Spacer';
import { convertMsToHms } from './utils';
import { useNavigate } from 'react-router-dom';

enum ANIMATION_EVENTS {
  SUB = 'SUB',
  BITS = 'BITS',
  BAN = 'BAN'
}

export const Animations = ({
  // timerMs
}:{
  // timerMs?: number
}) => {
  const [animation, setAnimation] = useState(ANIMATION_EVENTS.BAN);

  // const [latencyLLM, setLatencyLLM] = useState('');
  // const [latencyTTS, setLatencyTTS] = useState('');

  // useEffect(() => {
  //   const ws = new WebSocket('ws://localhost:4000');
  //   ws.addEventListener('open', () => {
  //     console.log('Connected to WebSocket server!');
  //   });
  //   ws.addEventListener('message', (_data) => {
  //     const data = JSON.parse(_data.data);
  //     if (data.hasOwnProperty('latency_llm')) {
  //       setLatencyLLM(data.latency_llm);
  //     }
  //     if (data.hasOwnProperty('latency_tts')) {
  //       setLatencyTTS(data.latency_tts);
  //     }
  //   });
  // }, []);

  let event = null;
  switch (animation) {
    case ANIMATION_EVENTS.SUB:
      event = (
        <div className='sub'>
          <div className='neon_text event_text_top'>
            NEW SUBSCRIBER&nbsp;&nbsp;<div className='ratjam-gif' />
          </div>
          <div className='neon_text event_text_middle'>Tier 3</div>
          <div className='neon_text event_text_bottom'>username</div>
        </div>
      );
      break;
      case ANIMATION_EVENTS.BITS:
        event = (
          <div className='bits'>
            <div className='neon_text event_text_top'>
              username just donated 100 bits!
            </div>
            <div className='rathole-gif' />
          </div>
        );
        break;
        case ANIMATION_EVENTS.BAN:
          event = (
            <div className='ban'>
              <div className='neon_text event_text_top'>
                username has been ejected into outer space!
              </div>
              <div className='ejection-gif' />
            </div>
            );
          break;
  }

  return (
    <div className='animations'>
      <Helmet><title>Heavenfire Animations</title></Helmet>

       <img
          className='stream_background_sample'
          alt='luna'
          src='stream_background_sample.png'
          width='1250px'
          height='800px'
        />

      <div className='event_container'>
        {event}
      </div>
    </div>
  );
};
