import './App.scss';
import { useRef, useEffect } from 'react';
import { Board } from './Board';
import { Tiles } from './Tiles';
import { Logs } from './Logs';
import { LetterDistribution } from './LetterDistribution';
import { tileMap } from '../game/tiles';
import { FlexContainer } from './FlexContainer';
import { Move } from '../game/types';
import { generateAIMove } from '../ai/generateAIMove';
import { generatePlayerMove } from '../ai/generatePlayerMove';
import { Spacer } from './Spacer';
import { ExchangeTilesModal } from './ExchangeTilesModal';
import { Button } from './Button';
import { fetch_post } from '../fetch_functions';
import { PRIORITY_QUEUE_PRIORITIES } from '../enums';
import { nanoid } from 'nanoid';
import { useReducer } from 'react';
import { initialState, reducer } from './app_reducer';

export const App = () => {
  const [state, dispatch] = useReducer(reducer, initialState);
  
  const utteranceIdRef = useRef('');
  const AIMoveRef = useRef<Move|null>(null);

  const AIPlayWordTimeoutRef = useRef<number | NodeJS.Timer>();

  const isActionDisabled = state.turn % 2 === 0 || state.isGameOver;
  const playerTileCount = state.playerTiles.filter(i => i !== null).length
  const AITileCount = state.AITiles.filter(i => i !== null).length
  // game over ondition #1: bag is empty, and one player's hand is empty.
  const condition1 = !state.bag.length && (!playerTileCount || !AITileCount);
  // game over condition #2: 6 turns have passed without any player gaining score.
  const condition2 = state.logs.slice(state.logs.length - 6).filter(log => !log.score).length === 6;

  const AIPlayWord = () => {
    // AI turn - play
    const processedAITiles:string[] = [];
    state.AITiles.forEach(i => {
      if (i !== null) {
        processedAITiles.push(i)
      }
    });
    processedAITiles.sort((a, b) => tileMap[b].points - tileMap[a].points);
    AIMoveRef.current = generateAIMove(state.placedTiles, processedAITiles);
    const aiMoveFriendlyString = AIMoveRef.current.words.map(
      tiles => tiles.map(tile => tile.letter.toLowerCase()).join('')
    ).join(', ');
    const utteranceId = nanoid();
    utteranceIdRef.current = utteranceId;
    // ENABLE BELOW LINE FOR LUNA INTEGRATION
    fetch_post('/receive_prompt', {
      prompt: `(you are currently playing scrabble). Announce that you just played: ${aiMoveFriendlyString}; for a total of ${AIMoveRef.current.score} points`,
      priority: PRIORITY_QUEUE_PRIORITIES.PRIORITY_MIC_INPUT,
      utterance_id: utteranceId
    });
    // OTHERWISE, ENABLE BELOW LINE
    // continueAIPlayWordAfterUtteranceIdReceived();
  };

  const continueAIPlayWordAfterUtteranceIdReceived = () => {
    const AIMove = AIMoveRef.current;
    if (AIMove) {
      dispatch({ type: 'continue_ai_play_word', payload: { AIMove } });
    } else {
      dispatch({ type: 'continue_ai_pass', payload: {} });
    }
  };

  const playerPlayWord = () => {
    if (isActionDisabled) {
      return;
    }

    const playerMove = generatePlayerMove(state.placedTiles, state.tempPlacedTiles)[0];
    if (playerMove) {
      // player turn - play
      dispatch({ type: 'player_play_word', payload: { playerMove} });
    } else {
      // player turn - play invalid word
      dispatch({
        type: 'unplace_selected_tiles',
        payload: { coordinates: Object.keys(state.tempPlacedTiles)}
      });
    }
  };

  const dispatchUnplaceSelectedTiles = (coordinates:string[]) => {
    dispatch({
      type: 'unplace_selected_tiles',
      payload: { coordinates }
    });
  };

  const dispatchPlaceSelectedTile = (x: number, y: number) => {
    dispatch({
      type: 'place_selected_tile',
      payload: { x, y }
    });
  };

  useEffect(() => {
    dispatch({ type: 'draw_tiles_at_start_of_game', payload: {} });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (condition1 || condition2) {
      fetch_post('/receive_prompt', {
        prompt: `(you are currently playing scrabble). You just won the game! Announce that you are the scrabble queen.`,
        priority: PRIORITY_QUEUE_PRIORITIES.PRIORITY_MIC_INPUT
      });
      dispatch({ type: 'set_game_over', payload: {} });
      return;
    } else if (state.turn % 2 === 0) {
      AIPlayWordTimeoutRef.current = setTimeout(() => {
        AIPlayWord();
      }, 100);
      // ^ this timeout duration must be a value greater than the time it takes setState() to run.
      // if 0, there's a race condition between whether AIPlayWord() is evaluated first, or setState() in playerPlayWord().
      // if not using setTimeout(), AIPlayWord() will always be evaluated before setState() in playerPlayWord(), meaning it would be impossible to set any states until AIPlayWord() finishes calculating.
      // if there was an easy way to utilize multithreading in React here, the setTimeout() would be unnecessary. there are some packages for this, but i didn't really want to download them.
      // so, for now, we just pray that setState() always finishes in less than 100ms, and just take the loss by having the AI turn be 100ms longer. (in the 0.01% chance setState takes longer than 100ms, the only negative effect would be the game UI would not update until the AI finishes its turn.)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.turn, condition1, condition2]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:4000');
    ws.addEventListener('open', () => {
      console.log('Connected to WebSocket server!');
    });
    ws.addEventListener('message', (_data) => {
      const data = JSON.parse(_data.data);
      if (data.hasOwnProperty('utterance_id') && data.utterance_id === utteranceIdRef.current) {
        utteranceIdRef.current = '';
        continueAIPlayWordAfterUtteranceIdReceived();
      }
    });

    return () => {
      clearTimeout(AIPlayWordTimeoutRef.current);
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className='app'>
      <div className='game'>        
        {state.isExchangeTilesModalOpen ? (
          <ExchangeTilesModal
            tiles={state.playerTiles}
            onExchangeClick={(selectedIndices:number[]) => dispatch({
              type: 'close_exchange_tiles_modal',
              payload: { selectedIndices }
            })}
            onCancelClick={() => dispatch({
              type: 'close_exchange_tiles_modal',
              payload: { selectedIndices: [] }
            })}
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
              <div className='score_text'>{state.playerTotalScore}</div>
            </FlexContainer>
            <FlexContainer
              className='scoreboard_half'
              flexDirection='column'
              alignItems='center'
              justifyContent='center'
            >
              <div className='score_player_name'>LUnA</div>
              <Spacer height={20} />
              <div className='score_text'>{state.AITotalScore}</div>
            </FlexContainer>
          </FlexContainer>
          <LetterDistribution placedTiles={state.placedTiles} />
        </FlexContainer>
        <FlexContainer
          className='board_and_tiles_container'
          flexDirection='column'
          justifyContent='center'
          alignItems='center'
        >
          <Tiles tiles={state.AITiles} areTilesHidden={true} />
          <Board
            placedTiles={state.placedTiles}
            tempPlacedTiles={state.tempPlacedTiles}
            placeSelectedTile={dispatchPlaceSelectedTile}
            unplaceSelectedTiles={dispatchUnplaceSelectedTiles}
          />
          <Tiles
            tiles={state.playerTiles}
            selectedTileIndices={[state.selectedTileIndex]}
            tileOnClick={(index:number) => dispatch({
              type: 'set_selected_tile_index',
              payload: { index }
            })}
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
          <Logs logs={state.logs} />
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
                onClick={() => dispatch({ type: 'open_exchange_tiles_modal', payload: {} })}
                isDisabled={state.bag.length === 0 || isActionDisabled}
              >
                Exchange (<span className='black_unicode_rectangle'>&#9646;</span>{state.bag.length})
              </Button>              
              <Spacer width={10} />
              <Button
                type='red'
                onClick={() => dispatch({ type: 'pass', payload: { player: 'player' }})}
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
