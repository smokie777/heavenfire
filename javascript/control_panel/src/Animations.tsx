import './Animations.scss';
import { Helmet } from 'react-helmet';
import { useEffect, useState, useRef } from 'react';
import { AnimationCascadingFadeInOut } from './AnimationCascadingFadeInOut';

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
  // const [twitchEvent, setTwitchEvent] = useState<twitchEvent | null>({
  //   event: 'BITS',
  //   username: 'test-username-for-bits',
  //   value: '2000'
  // });
  // const [twitchEvent, setTwitchEvent] = useState<twitchEvent | null>({
  //   event: 'SUB',
  //   username: 'test-username-for-sub',
  //   value: 'Prime'
  // });
  // const [twitchEvent, setTwitchEvent] = useState<twitchEvent | null>({
  //   event: 'BAN',
  //   username: 'test-username-for-ban',
  //   value: ''
  // });

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
        <AnimationCascadingFadeInOut
          className='sub'
          items={[
            <div className='neon_text event_text_top'>{twitchEvent.username}</div>,
            <div className='neon_text event_text_bottom'>{twitchEvent.value}</div>,
            <div className='ratsenteringhole-gif' />
          ]}
        />
      );
      break;
    case ANIMATION_EVENTS.BITS:
      event = (
        <AnimationCascadingFadeInOut
          className='bits'
          items={[
            <div className='neon_text event_text_top'>{twitchEvent.username}</div>,
            <div className='neon_text event_text_bottom'>
              <b>+</b>&nbsp;{twitchEvent.value}<div className='bits-png' />
            </div>,
            <div className='rathole-gif' />
          ]}
        />
      );
      break;
    case ANIMATION_EVENTS.BAN:
      event = (
        <AnimationCascadingFadeInOut
          className='ban'
          items={[
            <div className='neon_text event_text_top'>
              <b>{twitchEvent.username}</b> has been <b>ejected</b> into outer space!
            </div>,
            <div className='ejection-gif' />
          ]}
        />
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
