import './Logs.scss';
import { forEverySequencePermutation } from '../ai/forEverySequencePermutation';
import { twl06 } from '../game/twl06';
import { Log } from '../game/types';
import { createRef, useEffect } from 'react';

const fetchDictionaryEntry = async(word:string) => {
  // if the word contains blanks, just fetch the definition for one of the possible words.
  const wordWithBlanks = word;
  let wordWithoutBlanks = word;
  if (word.includes('_')) {
    const cb = (text:string) => {
      if (wordWithoutBlanks.includes('_') && twl06.hasOwnProperty(text)) {
        wordWithoutBlanks = text;
      }
    }
    forEverySequencePermutation(word, cb);
  }

  // fetch and alert the definition.
  const response = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${wordWithoutBlanks}`);
  const data = await response.json();
  const definitions:string[] = [];
  let numShownDefinitions = 0;
  let numTotalDefinitions = 0;

  if (response.status === 200) {
    data.forEach((entry:any) => {
      entry.meanings.forEach((meaning:any) => {
        numTotalDefinitions += meaning.definitions.length;
        numShownDefinitions++;
        definitions.push(`${meaning.partOfSpeech}: ${meaning.definitions[0].definition}`);
      });
    });
  } else {
    definitions.push('Error: no definitions found! Either the definition is really obscure, or the dictionary API errored out.')
    definitions.push('');
    definitions.push('You may want to consult a specific Scrabble dictionary (this project uses the twl06 word list).');
  }

  alert([
    wordWithBlanks === wordWithoutBlanks ? word : `${wordWithoutBlanks} (${wordWithBlanks})`,
    ...definitions,
    '',
    `Showing ${numShownDefinitions}/${numTotalDefinitions} definitions.`,
    'Source: Free Dictionary API: https://dictionaryapi.dev/'
  ].join('\n'));
};

const LogPlayerText = ({ player }:{ player:string }) => (
  <span style={{ color: player === 'player' ? 'seagreen' : 'red' }}>
    {player === 'player' ? 'Player' : 'Luna'}
  </span>
);

export const Logs = ({ logs }:{ logs:Log[] }) => {
  const logsComponentRef = createRef<HTMLDivElement>();
  
  useEffect(() => {
    // auto-scroll logs to bottom each time new log is added
    if (logsComponentRef.current) {
      logsComponentRef.current.scrollTop = logsComponentRef.current.scrollHeight;
    }
  });

  return (
    <div className='logs' ref={logsComponentRef}>
      {logs.map((log, index) => {
        let logContents = null;
        if (log.action === 'move') {
          logContents = (
            <>
              <span className='bold'>Turn {log.turn}: </span>
              <LogPlayerText player={log.player} /> played {(log.words || []).map((i, index) => (
                <span key={index}>
                  <span
                    className='dictionary_api_connected_word'
                    onClick={() => fetchDictionaryEntry(i.word)}
                  >
                  {i.word}
                  </span>
                  <span> ({i.score} pts){index === (log.words || []).length - 1 ? null : ' + '}</span>
                </span>
              ))}
              {log.isBingo ? <span> + <span className='bingo'>Bingo Bonus!</span> (50)</span> : null}
              &nbsp;= ({log.score} pts)
            </>
          );
        } else if (log.action === 'pass') {
          logContents = (
            <>
              <span className='bold'>Turn {log.turn}: </span>
              <LogPlayerText player={log.player} /> passed.
            </>
          );
        } else if (log.action === 'exchange') {
          logContents = (
            <>
              <span className='bold'>Turn {log.turn}: </span>
              <LogPlayerText player={log.player} /> exchanged tiles.
            </>
          );
        } else if (log.action === 'win_condition_1') {
          logContents = (
            <>
              <span className='gameover'>Game over - the bag is empty, and <LogPlayerText player={log.player} /> has played all their tiles!</span>
            </>
          );
        } else if (log.action === 'win_condition_2') {
          logContents = (
            <>
              <span className='gameover'>Game over - 0 points have been scored in the last 6 turns!</span>
            </>
          );
        } else if (log.action === 'score_penalty') {
          logContents = (
            <>
              <LogPlayerText player={log.player} /> receives (-{log.score} pts) from remaining unplayed tiles.
            </>
          );
        } else if (log.action === 'score_bonus') {
          logContents = (
            <>
              <LogPlayerText player={log.player} /> receives (+{log.score} pts) from <LogPlayerText player={log.player === 'player' ? 'AI' : 'player'} />'s unplayed tiles.
            </>
          );
        } else if (log.action === 'winner') {
          logContents = log.player ? (
            <>
              <LogPlayerText player={log.player} /><span className='gameover'> has won!</span>
            </>
          ) : (
            <span className='gameover'>It's a tie!</span>
          );
        }

        return (
          <div key={index} className='log'>
            {logContents}
          </div>
        );
      })}
    </div>
  );
};
