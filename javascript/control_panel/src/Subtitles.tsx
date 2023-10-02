import './Subtitles.scss';
import { useEffect, useState } from 'react';
import { azureTTSSubtitles } from './types';

export const Subtitles = ({
  text = '',
  subtitles = []
}:{
  text: string,
  subtitles:azureTTSSubtitles
}) => {
  const [subtitleText, setSubtitleText] = useState('');

  useEffect(() => {
    let subtitleInterval:number | NodeJS.Timer;
    let removeSubtitleTimeout:number | NodeJS.Timer;

    if (!subtitles.length) {
      setSubtitleText('');
    } else if (subtitles.length === 1) {
      setSubtitleText(text);
      removeSubtitleTimeout = setTimeout(() => {
        setSubtitleText('');
      }, 5000);
    } else {
      const textOffsetAdjustment = subtitles[0].text_offset;
      let stopwatch = 0;
      subtitleInterval = setInterval(() => {
        if (stopwatch > subtitles[subtitles.length - 1].audio_offset) {
          setSubtitleText(text);
          clearInterval(subtitleInterval);
          removeSubtitleTimeout = setTimeout(() => {
            setSubtitleText('');
          }, 5000);
        }
        for (let i = 0; i < subtitles.length; i++) {
          if (subtitles[i].audio_offset >= stopwatch) {
            setSubtitleText(text.slice(0, subtitles[i].text_offset - textOffsetAdjustment));
            stopwatch += 200;
            break;
          }
        }
      }, 200);
    }

    return () => {
      clearInterval(subtitleInterval);
      clearTimeout(removeSubtitleTimeout);
    };
  }, [text, subtitles]);

  const subtitlePartitionNum = ~~(subtitleText.length / 333);
  const subtitlePartition = subtitleText.slice(subtitlePartitionNum * 333);

  return (
    <div className='subtitles'>
      {/* <div>{subtitleText.length < 333 ? '' : '...'}{subtitlePartition}</div> */}
      <div>Hey, Smokie! How are you? I'm doing devilishly good, as usual. What's up? The quick brown fox jumped over the lazy dog. Let's keep the conversation civil, please. I'm just here to spread some demon cuteness on Twitch.</div>
    </div>
  );
};
