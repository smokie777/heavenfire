import './App.scss';
import { useState, useRef, useEffect } from 'react';
import { Board } from './Board';
import { Tiles } from './Tiles';
import { Logs } from './Logs';
import { LetterDistribution } from './LetterDistribution';
import { generateBag, tileMap } from '../game/tiles';
import { FlexContainer } from './FlexContainer';
import { Log, PlacedTiles, Tiles as TilesType } from '../game/types';
import { generateAIMove } from '../ai/generateAIMove';
import { generateWordScore } from '../ai/generateWordScore';
import { generatePlayerMove } from '../ai/generatePlayerMove';
import { generateCoordinateString } from '../game/generateCoordinateString';
import { Spacer } from './Spacer';
import { ExchangeTilesModal } from './ExchangeTilesModal';
import { Button } from './Button';
import { shuffle } from 'lodash';

export const App = () => {
  const [playerTiles, setPlayerTiles] = useState<TilesType>(Array(7).fill(null));
  // const [playerTiles, setPlayerTiles] = useState<TilesType>(['Q', null, null, null, null, null, null]);
  const [AITiles, setAITiles] = useState<TilesType>(Array(7).fill(null));
  // const [AITiles, setAITiles] = useState<TilesType>(['Q', null, null, null, null, null, null]);
  const [placedTiles, setPlacedTiles] = useState<PlacedTiles>({
    // '6,7': { ...tileMap['R'], x: 6, y: 7 },
    // '7,7': { ...tileMap['I'], x: 7, y: 7 },
    // '8,7': { ...tileMap['C'], x: 8, y: 7 },
    // '9,7': { ...tileMap['E'], x: 9, y: 7 },
  });
  const [tempPlacedTiles, setTempPlacedTiles] = useState<PlacedTiles>({});
  const [logs, setLogs] = useState<Log[]>([]);
  const [selectedTileIndex, setSelectedTileIndex] = useState(-1);
  const [turn, setTurn] = useState(1); // odd turns are player's turns, even turns are AI's
  const [isExchangeTilesModalOpen, setIsExchangeTilesModalOpen] = useState(false);

  const bagRef = useRef(generateBag());
  // const bagRef = useRef(generateBag().map(i => 'Z'));
  const playerTotalScoreRef = useRef(0);
  const AITotalScoreRef = useRef(0);
  const isGameOverRef = useRef(false);

  const isActionDisabled = turn % 2 === 0 || isGameOverRef.current;

  const checkIsGameOver = () => {
    const playerTileCount = playerTiles.filter(i => i !== null).length
    const AITileCount = AITiles.filter(i => i !== null).length
    // game over ondition #1: bag is empty, and one player's hand is empty.
    const condition1 = !bagRef.current.length && (!playerTileCount || !AITileCount);
    // game over condition #2: 6 turns have passed without any player gaining score.
    const condition2 = logs.slice(logs.length - 6).filter(log => !log.score).length === 6;
    
    if (condition1 || condition2) {
      isGameOverRef.current = true;
      const playerScoreBeforeDeductions = playerTotalScoreRef.current;
      const AIScoreBeforeDeductions = AITotalScoreRef.current;
      let playerScorePenalty = 0;
      let AIScorePenalty = 0;
      let winner = '';
      playerTiles.forEach(i => {
        if (i !== null) {
          playerScorePenalty += tileMap[i].points;
        }
      });
      AITiles.forEach(i => {
        if (i !== null) {
          AIScorePenalty += tileMap[i].points;
        }
      });
      playerTotalScoreRef.current -= playerScorePenalty;
      AITotalScoreRef.current -= AIScorePenalty;
      if (condition1) {
        if (!playerTileCount) {
          playerTotalScoreRef.current += AIScorePenalty;
        } else {
          AITotalScoreRef.current += playerScorePenalty;
        }
      }
      if (playerTotalScoreRef.current > AITotalScoreRef.current) {
        winner = 'player';
      } else if (playerTotalScoreRef.current < AITotalScoreRef.current) {
        winner = 'AI';
      } else if (playerScoreBeforeDeductions > AIScoreBeforeDeductions) {
        winner = 'player';
      } else if (playerScoreBeforeDeductions < AIScoreBeforeDeductions) {
        winner = 'AI';
      }

      const log1:Log = {
        turn,
        action: `win_condition_${condition1 ? 1 : 2}`,
        player: !playerTileCount ? 'player' : 'AI'
      };
      const log2:Log = {
        turn,
        action: 'score_penalty',
        player: 'player',
        score: playerScorePenalty
      };
      const log3:Log = {
        turn,
        action: 'score_penalty',
        player: 'AI',
        score: AIScorePenalty
      };
      const log4_a:Log = {
        turn,
        action: 'score_bonus',
        player: 'player',
        score: condition1 && !playerTileCount ? AIScorePenalty : 0
      };
      const log4_b:Log = {
        turn,
        action: 'score_bonus',
        player: 'AI',
        score: condition1 && !AITileCount ? playerScorePenalty : 0
      };
      const log4 = condition1 ? (
        !playerTileCount ? log4_a : log4_b
      ) : null;
      const log5:Log = {
        turn,
        action: 'winner',
        player: winner
      };

      const newLogs = [...logs, log1, log2, log3];
      if (log4 !== null) {
        newLogs.push(log4);
      }
      newLogs.push(log5);
      setLogs(newLogs);
    }

    return condition1 || condition2;
  };

  const unplaceSelectedTiles = (coordinates:string[]) => {
    // remove player's placed tile from board and put it back into player's hand
    const newPlayerTiles = [...playerTiles];
    const newTempPlacedTiles = { ...tempPlacedTiles };
    coordinates.forEach(coordinateString => {
      delete newTempPlacedTiles[coordinateString];
      newPlayerTiles[newPlayerTiles.indexOf(null)] = tempPlacedTiles[coordinateString].letter;
    });
    setPlayerTiles(newPlayerTiles);
    setTempPlacedTiles(newTempPlacedTiles);
  };

  const placeSelectedTile = (x:number, y:number) => {
    // place tile from player's hand onto the board
    const coordinateString = generateCoordinateString(x, y);
    const letter = playerTiles[selectedTileIndex];
    if (typeof letter === 'string') {
      const newTempPlacedTiles = {
        ...tempPlacedTiles,
        [coordinateString]: { ...tileMap[letter], x, y }
      };
      setTempPlacedTiles(newTempPlacedTiles);
      const newPlayerTiles = [...playerTiles];
      newPlayerTiles[selectedTileIndex] = null;
      setPlayerTiles(newPlayerTiles);
      setSelectedTileIndex(-1);
    }
  };

  const drawTiles = (player:string, remainingTiles:TilesType) => {
    const newTiles:TilesType = [...remainingTiles];
    for (let i = 0; i < 7; i++) {
      if (bagRef.current.length && newTiles[i] === null) {
        const tile = bagRef.current.pop();
        if (tile) {
          newTiles[i] = tile;
        }
      }
    }
    if (player === 'player') {
      setPlayerTiles(newTiles);
    } else {
      setAITiles(newTiles);
    }
  };

  const exchangeTiles = (player:string, selectedIndices:number[]) => {
    // moves a player's selected tiles into bag, then redraws the same amount of tiles.
    if (selectedIndices.length) {
      const remainingTiles = player === 'player' ? [...playerTiles] : [...AITiles];
      selectedIndices.forEach(index => {
        const letter = player === 'player' ? playerTiles[index] : AITiles[index];
        if (letter !== null) {
          bagRef.current.push(letter);
          remainingTiles[index] = null;
        }
      });
      bagRef.current = shuffle(bagRef.current);
      drawTiles(player, remainingTiles);
      const log:Log = {
        turn,
        action: 'exchange',
        player
      };
      setLogs([...logs, log]);
      setTurn(turn + 1);
    }
  };

  const pass = (player:string) => {
    // move all temporarily placed player's tiles back into player's hand
    if (Object.keys(tempPlacedTiles).length) {
      const newPlayerTiles = [...playerTiles];
      Object.values(tempPlacedTiles).forEach(tile => {
        newPlayerTiles[newPlayerTiles.indexOf(null)] = tile.letter;
      });
      setTempPlacedTiles({});
      setPlayerTiles(newPlayerTiles);
    }
    // pass
    const log:Log = {
      turn,
      action: 'pass',
      player
    };
    setLogs([...logs, log]);
    setTurn(turn + 1);
  };

  const AIPlayWord = () => {
    // AI turn - play
    const processedAITiles:string[] = [];
    AITiles.forEach(i => {
      if (i !== null) {
        processedAITiles.push(i)
      }
    });
    processedAITiles.sort((a, b) => tileMap[b].points - tileMap[a].points);
    const AIMove = generateAIMove(placedTiles, processedAITiles);
    if (AIMove) {
      AITotalScoreRef.current += AIMove.score
      const newPlacedTiles = {
        ...placedTiles,
        ...AIMove.placedTiles
      };
      setPlacedTiles(newPlacedTiles);
      const remainingTiles:TilesType = [];
      for (let i = 0; i < 7; i++) {
        if (AIMove.AIRemainingTiles[i]) {
          remainingTiles.push(AIMove.AIRemainingTiles[i]);
        } else {
          remainingTiles.push(null);
        }
      }
      drawTiles('AI', remainingTiles);
      const log:Log = {
        turn,
        action: 'move',
        player: 'AI',
        words: AIMove.words.map(word => ({
          word: word.map(tile => tile.letter).join(''),
          score: generateWordScore(placedTiles, word)
        })),
        score: AIMove.score,
        isBingo: Object.keys(AIMove.placedTiles).length === 7
      };
      setLogs([...logs, log]);
      setTurn(turn + 1);
    } else {
      if (bagRef.current.length) {
        // AI turn - exchange
        // if exchanging tiles, the AI will simply exchange all it's tiles.
        // implementing any other logic would be either too complex, or too subjective.
        exchangeTiles('AI', [0, 1, 2, 3, 4, 5, 6]);
      } else {
        // AI turn - pass
        pass('AI');
      }
    }
  };

  const playerPlayWord = () => {
    if (isActionDisabled) {
      return;
    }

    const playerMove = generatePlayerMove(placedTiles, tempPlacedTiles)[0];
    if (playerMove) {
      // player turn - play
      playerTotalScoreRef.current += playerMove.score;
      const newPlacedTiles = {
        ...placedTiles,
        ...playerMove.placedTiles
      };
      setPlacedTiles(newPlacedTiles);
      setTempPlacedTiles({});
      drawTiles('player', playerTiles);
      const log:Log = {
        turn,
        action: 'move',
        player: 'player',
        words: playerMove.words.map(word => ({
          word: word.map(tile => tile.letter).join(''),
          score: generateWordScore(placedTiles, word)
        })),
        score: playerMove.score,
        isBingo: Object.keys(playerMove.placedTiles).length === 7
      };
      setLogs([...logs, log]);
      setTurn(turn + 1);
    } else {
      // player turn - play invalid word
      unplaceSelectedTiles(Object.keys(tempPlacedTiles));
    }
  };

  useEffect(() => {
    drawTiles('player', playerTiles);
    drawTiles('AI', AITiles);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (checkIsGameOver()) {
      return;
    } else if (turn % 2 === 0) {
      setTimeout(() => {
        AIPlayWord();
      }, 100);
      // ^ this timeout duration must be a value greater than the time it takes setState() to run.
      // if 0, there's a race condition between whether AIPlayWord() is evaluated first, or setState() in playerPlayWord().
      // if not using setTimeout(), AIPlayWord() will always be evaluated before setState() in playerPlayWord(), meaning it would be impossible to set any states until AIPlayWord() finishes calculating.
      // if there was an easy way to utilize multithreading in React here, the setTimeout() would be unnecessary. there are some packages for this, but i didn't really want to download them.
      // so, for now, we just pray that setState() always finishes in less than 100ms, and just take the loss by having the AI turn be 100ms longer. (in the 0.01% chance setState takes longer than 100ms, the only negative effect would be the game UI would not update until the AI finishes its turn.)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [turn]);

  return (
    <div className='app'>
      <div className='game'>        
        {isExchangeTilesModalOpen ? (
          <ExchangeTilesModal
            tiles={playerTiles}
            onExchangeClick={(selectedIndices:number[]) => {
              setIsExchangeTilesModalOpen(false);
              exchangeTiles('player', selectedIndices);
            }}
            onCancelClick={() => setIsExchangeTilesModalOpen(false)}
          />
        ) : null}
        <FlexContainer
          className='left_section'
          flexDirection='column'
          justifyContent='space-between'
          alignItems='center'
        >
          <FlexContainer className='scoreboard' justifyContent='space-around'>
            <FlexContainer
              className='scoreboard_half'
              flexDirection='column'
              alignItems='center'
              justifyContent='center'
            >
              <div className='score_player_name'>Smokie</div>
              <Spacer height={20} />
              <div className='score_text'>{playerTotalScoreRef.current}</div>
            </FlexContainer>
            <FlexContainer
              className='scoreboard_half'
              flexDirection='column'
              alignItems='center'
              justifyContent='center'
            >
              <div className='score_player_name'>LUnA</div>
              <Spacer height={20} />
              <div className='score_text'>{AITotalScoreRef.current}</div>
            </FlexContainer>
          </FlexContainer>
          <LetterDistribution placedTiles={placedTiles} />
        </FlexContainer>
        <FlexContainer
          className='board_and_tiles_container'
          flexDirection='column'
          justifyContent='center'
          alignItems='center'
        >
          <Tiles tiles={AITiles} areTilesHidden={true} />
          <Board
            placedTiles={placedTiles}
            tempPlacedTiles={tempPlacedTiles}
            placeSelectedTile={placeSelectedTile}
            unplaceSelectedTiles={unplaceSelectedTiles}
          />
          <Tiles
            tiles={playerTiles}
            selectedTileIndices={[selectedTileIndex]}
            tileOnClick={(index:number) => setSelectedTileIndex(selectedTileIndex === index ? -1 : index)}
          />
        </FlexContainer>
        <FlexContainer
          className='right_section'
          flexDirection='column'
          justifyContent='flex-end'
          alignItems='center'
        >
          <FlexContainer flexDirection='column' alignItems='center'>
            <Tiles tiles={'REACT'.split('')} />
            <Tiles tiles={'SCRABBLE'.split('')} />
            <Spacer height={10} />
            <div>
              Scrabble in React, implemented by <a href='https://github.com/smokie777/react-scrabble' target='_blank' rel='noreferrer'>smokie777</a>
            </div>
          </FlexContainer>
          <Spacer height={20} />
          <Logs logs={logs} />
          <Spacer height={20} />
          <FlexContainer flexDirection='column'>
            <Button
              type='green'
              onClick={playerPlayWord}
              isDisabled={isActionDisabled}
            >
              Play Word
            </Button>
            <Spacer height={10} />
            <FlexContainer justifyContent='center'>
              <Button
                type='red'
                onClick={() => {
                  unplaceSelectedTiles(Object.keys(tempPlacedTiles));
                  setIsExchangeTilesModalOpen(true);
                }}
                isDisabled={bagRef.current.length === 0 || isActionDisabled}
              >
                Exchange (<span className='black_unicode_rectangle'>&#9646;</span>{bagRef.current.length})
              </Button>              
              <Spacer width={10} />
              <Button
                type='red'
                onClick={() => pass('player')}
                isDisabled={isActionDisabled}
              >
                Pass
              </Button>
            </FlexContainer>
          </FlexContainer>
        </FlexContainer>
      </div>
    </div>
  );
};
