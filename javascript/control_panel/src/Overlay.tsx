import './Overlay.scss';
import { Helmet } from 'react-helmet';
import { useEffect, useState, useRef } from 'react';
import { Spacer } from './Spacer';
import { convertMsToHms } from './utils';
import { useNavigate } from 'react-router-dom';

export const OverlayTimer = ({
  ms
}:{
  ms: number
}) => {
  const redirectTimeoutRef = useRef<number | NodeJS.Timer>();
  const tickIntervalRef = useRef<number | NodeJS.Timer>();
  const [timerMs, setTimerMs] = useState(ms);
  const navigate = useNavigate();
  
  const hms = convertMsToHms(timerMs);

  useEffect(() => {
    tickIntervalRef.current = setInterval(() => {
      setTimerMs((timerMs) => {
        const newTimerMs = timerMs - 1000;
        if (!newTimerMs) {
          clearInterval(tickIntervalRef.current);
          redirectTimeoutRef.current = setTimeout(() => {
            navigate('/overlay');
          }, 5000);
        }
        return newTimerMs;
      });
    }, 1000);

    return () => {
      clearInterval(tickIntervalRef.current);
      clearTimeout(redirectTimeoutRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const h = `${hms.h.toString().length === 1 ? '0' : ''}${hms.h.toString()}`;
  const m = `${hms.m.toString().length === 1 ? '0' : ''}${hms.m.toString()}`;
  const s = `${hms.s.toString().length === 1 ? '0' : ''}${hms.s.toString()}`;
  
  return (
    <div className='timer_numbers neon_text'>
      {!!hms.h && `${h}:`}{m}:{s}
    </div>
  )
};

export const Overlay = ({
  timerMs
}:{
  timerMs?: number
}) => {
  const [latencyLLM, setLatencyLLM] = useState('');
  const [latencyTTS, setLatencyTTS] = useState('');

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:4000');
    ws.addEventListener('open', () => {
      console.log('Connected to WebSocket server!');
    });
    ws.addEventListener('message', (_data) => {
      const data = JSON.parse(_data.data);
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

      {!!timerMs && (
        <div className='timer_container'>        
          <div className='timer_text neon_text'>Stream starting soon!</div>
          <OverlayTimer ms={timerMs} />
        </div>
      )}

      <div className='live_container'>
        <div className='live_dot' />
        <div className='live_text neon_text'>live</div>
      </div>

      <div className='logo_container'>
        <div className='logo neon_text'>&nbsp;Welcome</div>
        <div className='logo_sub neon_text'>to the Smokie n Luna stream! 🖤✨</div>
        <div className='logo_sub_sub neon_text'>← Luna, an AI</div> 
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
        <div className='latency_title neon_text'>Luna latency</div>
        <div className='neon_underline neon_box' />
        <Spacer height={10} />
        <div className='latency_item neon_text'>LLM: {latencyLLM || '-'}</div>
        <div className='latency_item neon_text'>TTS: {latencyTTS || '-'}</div>
      </div>
    </div>
  );
};
