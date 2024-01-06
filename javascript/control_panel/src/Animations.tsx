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
  const isAnimationInProgressRef = useRef(false);
  const twitchEventQueueRef = useRef<twitchEvent[]>([]);
  const [twitchEvent, setTwitchEvent] = useState<twitchEvent | undefined>(undefined);
  // const [twitchEvent, setTwitchEvent] = useState<twitchEvent | undefined>({
  //   event: 'BITS',
  //   username: 'test-username-for-bits',
  //   value: '2000'
  // });
  // const [twitchEvent, setTwitchEvent] = useState<twitchEvent | undefined>({
  //   event: 'SUB',
  //   username: 'test-username-for-sub',
  //   value: 'Prime'
  // });
  // const [twitchEvent, setTwitchEvent] = useState<twitchEvent | undefined>({
  //   event: 'BAN',
  //   username: 'test-username-for-ban',
  //   value: ''
  // });

  const runTwitchEventQueue = () => {
    isAnimationInProgressRef.current = true;
    const event = twitchEventQueueRef.current.shift();
    setTwitchEvent(event);
    if (event) {
      clearAnimationTimeoutRef.current = setTimeout(() => {
        runTwitchEventQueue();
      }, 10000);
    } else {
      isAnimationInProgressRef.current = false;
    }
  };

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:4000');
    ws.addEventListener('open', () => {
      console.log('Connected to WebSocket server!');
    });
    ws.addEventListener('message', (_data) => {
      const data = JSON.parse(_data.data);
      if (data.hasOwnProperty('twitch_event')) {
        twitchEventQueueRef.current.push(data.twitch_event);
        if (!isAnimationInProgressRef.current) {
          runTwitchEventQueue();
        }
      }
    });

    return () => {
      clearTimeout(clearAnimationTimeoutRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  let event;
  switch (twitchEvent?.event) {
    case ANIMATION_EVENTS.SUB:
      event = (
        <AnimationCascadingFadeInOut
          key={new Date().toLocaleString()}
          className='sub'
          items={[
            <div className='subtitle_text event_text_top'>{twitchEvent.username}</div>,
            <div className='subtitle_text event_text_bottom'>{twitchEvent.value}</div>,
            <div className='ratsenteringhole-gif' />
          ]}
        />
      );
      break;
    case ANIMATION_EVENTS.BITS:
      event = (
        <AnimationCascadingFadeInOut
          key={new Date().toLocaleString()}
          className='bits'
          items={[
            <div className='subtitle_text event_text_top'>{twitchEvent.username}</div>,
            <div className='subtitle_text event_text_bottom'>
              just donated {twitchEvent.value}<div className='bits-png' />!
            </div>,
            <div className='rathole-gif' />
          ]}
        />
      );
      break;
    case ANIMATION_EVENTS.BAN:
      event = (
        <AnimationCascadingFadeInOut
          key={new Date().toLocaleString()}
          className='ban'
          items={[
            <div className='subtitle_text event_text_top'>{twitchEvent.username}</div>,
            <div className='subtitle_text event_text_bottom'>
              has been <b>ejected</b> into outer space!
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

      <div className='event_container'>
        {event}
      </div>
    </div>
  );
};
