import './Animations.scss';
import { Helmet } from 'react-helmet';
import { useEffect, useState, useRef } from 'react';
import { Spacer } from './Spacer';
import { convertMsToHms } from './utils';
import { useNavigate } from 'react-router-dom';

export const Animations = ({
  // timerMs
}:{
  // timerMs?: number
}) => {
  // const [latencyLLM, setLatencyLLM] = useState('');
  // const [latencyTTS, setLatencyTTS] = useState('');

  // useEffect(() => {
  //   const ws = new WebSocket('ws://localhost:4000');
  //   ws.addEventListener('open', () => {
  //     console.log('Connected to WebSocket server!');
  //   });
  //   ws.addEventListener('message', (_data) => {
  //     const data = JSON.parse(_data.data);
  //     console.log(data);
  //     if (data.hasOwnProperty('latency_llm')) {
  //       setLatencyLLM(data.latency_llm);
  //     }
  //     if (data.hasOwnProperty('latency_tts')) {
  //       setLatencyTTS(data.latency_tts);
  //     }
  //   });
  // }, []);

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

      <div className='text_container'>
        <div className='neon_text event_text_top'>
          NEW SUBSCRIBER<div className='ratjam-gif' />
        </div>
        <div className='neon_text event_text_middle'>Tier 3</div>
        <div className='neon_text event_text_bottom'>coption1</div>
      </div>
    </div>
  );
};
