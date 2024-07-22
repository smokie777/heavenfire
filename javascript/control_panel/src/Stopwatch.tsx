import './Stopwatch.scss';
import { useEffect, useRef, useState } from 'react';
import { Helmet } from 'react-helmet';

const MAX_STOPWATCH_MS = 1000 * 60 * 60 * 24; // 24 hours

export const Stopwatch = () => {
  const animationRef = useRef<number | null>(null);
  const timestampStartRef = useRef(0);
  const [isStarted, setIsStarted] = useState(false);

  const timerAnimation = (timestamp:number) => {
    if (!timestampStartRef.current) {
      timestampStartRef.current = timestamp;
    }
    const totalMs = timestamp - timestampStartRef.current;
    const totalS = totalMs / 1000;
    const totalM = totalS / 60;
    const totalH = totalM / 60;
    const displayMs = ~~((totalMs % 1000) / 10);
    const displayS = ~~(totalS) % 60;
    const displayM = ~~(totalM) % 60;
    const displayH = ~~(totalH);
    const elHms = document.getElementById('stopwatch_text--hms');
    const elMs = document.getElementById('stopwatch_text--ms');
    if (elHms) {
      elHms.textContent = `${displayH < 10 ? '0' : ''}${displayH}:${displayM < 10 ? '0' : ''}${displayM}:${displayS < 10 ? '0' : ''}${displayS}`;
    }
    if (elMs) {
      elMs.textContent = `.${displayMs < 10 ? '0' : ''}${displayMs}`
    }
    if (totalMs < MAX_STOPWATCH_MS) {
      animationRef.current = requestAnimationFrame(timerAnimation);
    }
  };
    
  const startOrPauseTimer = () => {
    if (!isStarted) {
      animationRef.current = requestAnimationFrame(timerAnimation);
    } else {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    }
    setIsStarted(!isStarted);
  };

  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <div className='stopwatch'>
      <Helmet><title>Heavenfire Stopwatch</title></Helmet>

      <div className='stopwatch_container'>
        <div className='stopwatch_text_container'>
          <span className='stopwatch_text' id='stopwatch_text--hms'>00:00:00</span>
          <span className='stopwatch_text' id='stopwatch_text--ms'>.00</span>
        </div>
        <br />
        <button onClick={startOrPauseTimer}>{isStarted ? 'pause' : 'start'}</button>
      </div>
    </div>
  );
};
