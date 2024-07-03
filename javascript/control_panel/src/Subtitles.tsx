import './Subtitles.scss';
import { useEffect, useState } from 'react';
import { azureTTSSubtitle } from './types';
import { useData } from './DataProvider';

export const Subtitles = ({
  text = '',
  subtitles = []
}:{
  text: string,
  subtitles:azureTTSSubtitle[]
}) => {
  const [subtitleText, setSubtitleText] = useState('');
  const { data } = useData();

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
            setSubtitleText(
              (i >= 1 && subtitles[i - 1].text) // custom logic for hardcoded song subtitles
              || text.slice(0, subtitles[i].text_offset - textOffsetAdjustment) // normal logic
            );
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

  const subtitlePartitionsWith7tvEmotes = subtitlePartition.split(' ').map((text, index) => {
    if (data.emotesNameToUrlMap.hasOwnProperty(text)) {
      return (
        <div key={index} className='subtitle_text_inline_emote_container'>
          <img src={data.emotesNameToUrlMap[text]} alt={text} />&nbsp;
        </div>
      );
    } else {
      const commonPunctuationCharacters = ['.', '..', '...', '....', '?!', '!?', '!', '!!', '!!!', '!!!!', '?', '??', '???', '????'];
      for (let i = 0; i < commonPunctuationCharacters.length; i++) {
        const punc = commonPunctuationCharacters[i];
        const textSplit = text.split(punc);
        if (
          text.endsWith(punc)
          && (textSplit.length - 1) === 1
          && data.emotesNameToUrlMap.hasOwnProperty(textSplit[0])
        ) {
          return <>
            <div key={index} className='subtitle_text_inline_emote_container'>
              <img src={data.emotesNameToUrlMap[textSplit[0]]} alt={textSplit[0]} />&nbsp;
            </div>
            <div key={`${index}_${i}`}>{punc}&nbsp;</div>
          </>;
        }
      }
      return <div key={index}>{text}&nbsp;</div>;
    }
  });

  return (
    <div className='subtitles'>
      <div className='subtitle_text'>
        {subtitleText.length < 333 ? '' : '...'}
        {subtitlePartitionsWith7tvEmotes}
        {/* <div>What would I say if someone was trolling in my chat? I'd tell them to suck it!</div> */}
      </div>
    </div>
  );
};
