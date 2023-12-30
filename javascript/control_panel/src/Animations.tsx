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

interface twitchEvent {
  event: `${ANIMATION_EVENTS}`;
  username: string;
  value: string;
}

export const Animations = () => {
  const clearAnimationTimeoutRef = useRef<number | NodeJS.Timer>();
  const [twitchEvent, setTwitchEvent] = useState<twitchEvent | null>(null);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:4000');
    ws.addEventListener('open', () => {
      console.log('Connected to WebSocket server!');
    });
    ws.addEventListener('message', (_data) => {
      const data = JSON.parse(_data.data);
      if (
        data.hasOwnProperty('twitch_event')
        && !twitchEvent
      ) {
        setTwitchEvent(data.twitch_event);
        clearAnimationTimeoutRef.current = setTimeout(() => {
          setTwitchEvent(null);
        }, 10000);
      }
    });

    return () => {
      clearTimeout(clearAnimationTimeoutRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  let event = null;
  switch (twitchEvent?.event) {
    case ANIMATION_EVENTS.SUB:
      event = (
        <div className='sub'>
          <div className='neon_text event_text_top'>{twitchEvent.username}</div>
          <div className='neon_text event_text_bottom'>{twitchEvent.value}</div>
          <div className='ratsenteringhole-gif' />
        </div>
      );
      break;
    case ANIMATION_EVENTS.BITS:
      event = (
        <div className='bits'>
          <div className='neon_text event_text_top'>
            {twitchEvent.username} just donated {twitchEvent.value} bits!
          </div>
          <div className='rathole-gif' />
        </div>
      );
      break;
    case ANIMATION_EVENTS.BAN:
      event = (
        <div className='ban'>
          <div className='neon_text event_text_top'>
            {twitchEvent.username} has been ejected into outer space!
          </div>
          <div className='ejection-gif' />
        </div>
        );
      break;
    default:
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
