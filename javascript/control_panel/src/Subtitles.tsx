import './Subtitles.scss';
import { useEffect, useState } from 'react';

type azureTTSSubtitle = {
  audio_offset: number;
  text_offset: number;
};

export const Subtitles = ({
  text = '',
  subtitles = []
}:{
  text: string,
  subtitles:azureTTSSubtitle[]
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
      <div>{subtitleText.length < 333 ? '' : '...'}{subtitlePartition}</div>
      {/* <div>What would I say if doption1 was trolling in my chat? I'd tell doption1 to suck it!</div> */}
    </div>
  );
};
