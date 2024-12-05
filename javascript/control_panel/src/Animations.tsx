import './Animations.scss';
import { Helmet } from 'react-helmet';
import { useEffect, useState, useRef } from 'react';
import { AnimationCascadingFadeInOut } from './AnimationCascadingFadeInOut';
import { useData } from './DataProvider';
import { v4 as uuidv4 } from 'uuid';
import { extractFirst7tvEmote, getRandomNumberBetween } from './utils';
import { WEBSOCKET_EVENT_TYPES } from './enums';
import { Toast } from './Toast';

enum ANIMATION_EVENTS {
  SUB = 'SUB',
  BITS = 'BITS',
  BAN = 'BAN',
  MESSAGE = 'MESSAGE'
}

interface TwitchEvent {
  event: `${ANIMATION_EVENTS}`;
  username: string;
  value: string;
}

interface Emote {
  id: string;
  text: string;
  createdAt: Date;
}

export const Animations = () => {
  const wsRef = useRef<WebSocket | null>(null);
  const areLiveAnimatedEmotesOnRef = useRef(true);
  const liveAnimatedEmotes = useRef<Emote[]>([]);
  const clearEmotesIntervalRef = useRef<number | NodeJS.Timer>();
  const clearAnimationTimeoutRef = useRef<number | NodeJS.Timer>();
  const isAnimationInProgressRef = useRef(false);
  const twitchEventQueueRef = useRef<TwitchEvent[]>([]);
  const [twitchEvent, setTwitchEvent] = useState<TwitchEvent | undefined>(undefined);
  // const [twitchEvent, setTwitchEvent] = useState<TwitchEvent | undefined>({
  //   event: 'BITS',
  //   username: 'test-username-for-bits',
  //   value: '2000'
  // });
  // const [twitchEvent, setTwitchEvent] = useState<TwitchEvent | undefined>({
  //   event: 'SUB',
  //   username: 'test-username-for-sub',
  //   value: 'Prime'
  // });
  // const [twitchEvent, setTwitchEvent] = useState<TwitchEvent | undefined>({
  //   event: 'BAN',
  //   username: 'test-username-for-ban',
  //   value: ''
  // });
  const [toast, setToast] = useState('');
  const [rerenderIdenticalToastFlipper, setRerenderIdenticalToastFlipper] = useState(false);

  const { emotesNameToUrlMap } = useData();

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
    if (wsRef.current) {
      wsRef.current.close();
    }
    const ws = new WebSocket('ws://localhost:4000');
    wsRef.current = ws;
    ws.addEventListener('open', () => {
      console.log('Connected to WebSocket server!');
    });
    ws.addEventListener('message', (_data) => {
      const data = JSON.parse(_data.data);
      if (data.hasOwnProperty('twitch_event')) {
        const shouldUseTwitchEventQueue = data.twitch_event.event !== ANIMATION_EVENTS.MESSAGE;
        if (shouldUseTwitchEventQueue) {
          twitchEventQueueRef.current.push(data.twitch_event);
          if (!isAnimationInProgressRef.current) {
            runTwitchEventQueue();
          }
        } else if (areLiveAnimatedEmotesOnRef.current) {
          const maybeFirst7tvEmote = extractFirst7tvEmote(
            data.twitch_event.value,
            emotesNameToUrlMap
          );
          if (maybeFirst7tvEmote) {
            const emote = { id: uuidv4(), text: maybeFirst7tvEmote, createdAt: new Date() };
            liveAnimatedEmotes.current.push(emote);
            const container = document.getElementById('emotes_container');
            const img = document.createElement('img');
            img.setAttribute('class', 'emote');
            img.setAttribute('id', emote.id);
            img.setAttribute('src', emotesNameToUrlMap[maybeFirst7tvEmote]);
            img.setAttribute('alt', maybeFirst7tvEmote);
            // original css animation for 1440p monitor: moveX 2.25s linear 0s infinite alternate, moveY 4s linear 0s infinite alternate, vanish 15s linear 0s 1 forwards;
            // TODO: should probably refactor this to use requestAnimationFrame()
            // TODO: should also probably fix the bug that happens when you send the same emote twice in a row
            // TODO: should probably have this be in a separate component than the one that handles alerts
            // hooray, tech debt...
            img.style.animation = `moveX ${getRandomNumberBetween(1, 4)}s linear 0s infinite alternate, moveY ${getRandomNumberBetween(3, 6)}s linear 0s infinite alternate, vanish 10s linear 0s 1 forwards`;
            if (container) {
              container.appendChild(img);
            }
          }
        }
      } else if (data.type === WEBSOCKET_EVENT_TYPES['TOGGLE_LIVE_ANIMATED_EMOTES']) {
        if (areLiveAnimatedEmotesOnRef.current) {
          liveAnimatedEmotes.current.forEach(emote => {
            const el = document.getElementById(emote.id);
            el?.remove();
          });
          liveAnimatedEmotes.current = [];
        }
        areLiveAnimatedEmotesOnRef.current = !areLiveAnimatedEmotesOnRef.current;
      } else if (data.type === WEBSOCKET_EVENT_TYPES['TOGGLE_DVD']) {
        if (data.payload) {
          const container = document.getElementById('emotes_container');
          const img = document.createElement('img');
          img.setAttribute('class', 'emote');
          img.setAttribute('id', 'dvd');
          img.setAttribute('src', emotesNameToUrlMap['smokie40LunaPossessed']);
          img.setAttribute('alt', 'smokie40LunaPossessed');
          img.style.animation = 'moveX 4.5s linear 0s infinite alternate, moveY 8s linear 0s infinite alternate';
          if (container) {
            container.appendChild(img);
          }
        } else {
          const el = document.getElementById('dvd');
          el?.remove();
        }
      } else if (data.type === WEBSOCKET_EVENT_TYPES['SET_TOAST']) {
        if (data.payload) {
          setToast(data.payload);
          setRerenderIdenticalToastFlipper(prevState => !prevState);
        }
      }
    });

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      clearTimeout(clearAnimationTimeoutRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [emotesNameToUrlMap]);

  useEffect(() => {
    clearEmotesIntervalRef.current = setInterval(() => {
      if (liveAnimatedEmotes.current.length) {
        const currentTime = new Date();
        const tenSecondsAgo = new Date(currentTime.getTime() - 10000);
        const newLiveAnimatedEmotes:Emote[] = [];
        liveAnimatedEmotes.current.forEach(emote => {
          if (emote.createdAt < tenSecondsAgo) {
            const el = document.getElementById(emote.id);
            el?.remove();
          } else {
            newLiveAnimatedEmotes.push(emote);
          }
        });
        liveAnimatedEmotes.current = newLiveAnimatedEmotes;
      }

      return () => {
        clearInterval(clearAnimationTimeoutRef.current);
      };
    }, 1000);
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
            // <div className='ratsenteringhole-gif' />,
            <div className='lunaspin-gif' />
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
              has been&nbsp;<b>ejected</b>&nbsp;into outer space!
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

      <div className='emotes_container' id='emotes_container' />

      <div className='event_container'>
        {event}
      </div>

      <Toast toast={toast} rerenderIdenticalToastFlipper={rerenderIdenticalToastFlipper} />
    </div>
  );
};
