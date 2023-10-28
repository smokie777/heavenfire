import './Overlay.scss';
import { Helmet } from 'react-helmet';
import { useEffect, useState } from 'react';
import { Spacer } from './Spacer';

export const Overlay = () => {
  const [latencyLLM, setLatencyLLM] = useState('');
  const [latencyTTS, setLatencyTTS] = useState('');

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:4000');
    ws.addEventListener('open', () => {
      console.log('Connected to WebSocket server!');
    });
    ws.addEventListener('message', (_data) => {
      const data = JSON.parse(_data.data);
      console.log(data);
      if (data.hasOwnProperty('latency_llm')) {
        setLatencyLLM(data.latency_llm);
      }
      if (data.hasOwnProperty('latency_tts')) {
        setLatencyTTS(data.latency_tts);
      }
    });
  }, []);

  return (
    <div className='overlay'>
      <Helmet><title>Heavenfire Overlay</title></Helmet>

      <div className='live_container'>
        <div className='live_dot' />
        <div className='live_text neon_text'>live</div>
      </div>
      
      <div className='chat_widget'>
        <div className='chat_widget_top'>
          <div className='neon_underline neon_box' />
        </div>
        <div className='chat_widget_bottom'>
          <div className='neon_underline neon_box' />
          <div className='chat_input neon_text'>Chat:<div className='blinking_vertical_bar neon_box' /></div>
          <div className='neon_underline neon_box' />
        </div>
      </div>

      <div className='latency'>
        <div className='latency_title neon_text'>Latency</div>
        <div className='neon_underline neon_box' />
        <Spacer height={10} />
        <div className='latency_item neon_text'>LLM: {latencyLLM || '-'}</div>
        <div className='latency_item neon_text'>TTS: {latencyTTS || '-'}</div>
      </div>
    </div>
  );
};
