import { shuffle } from 'lodash';
import { generateWordScore } from '../ai/generateWordScore';
import { generateBag } from '../game/tiles';
import { Log, Move, PlacedTiles, Tiles as TilesType } from '../game/types';
import { generateCoordinateString } from '../game/generateCoordinateString';
import { tileMap } from '../game/tiles';

type Action =
  | { type: 'continue_ai_play_word', payload: { AIMove: Move } }
  | { type: 'continue_ai_pass', payload: {} }
  | { type: 'player_play_word', payload: { playerMove: Move } }
  | { type: 'draw_tiles_at_start_of_game', payload: {} }
  | { type: 'unplace_selected_tiles', payload: { coordinates: string[] } }
  | { type: 'place_selected_tile', payload: { x: number, y: number } }
  | { type: 'open_exchange_tiles_modal', payload: {} }
  | { type: 'pass', payload: { player: string } }
  | { type: 'set_selected_tile_index', payload: { index: number }}
  | { type: 'close_exchange_tiles_modal', payload: { selectedIndices: number[] }}
  | { type: 'set_game_over', payload: {}}
;

interface State {
  playerTiles: TilesType;
  AITiles: TilesType;
  placedTiles: PlacedTiles;
  tempPlacedTiles: PlacedTiles;
  logs: Log[];
  selectedTileIndex: number;
  turn: number;
  isExchangeTilesModalOpen: boolean;

  // these below variables were previously refs.
  bag: string[];
  playerTotalScore: number;
  AITotalScore: number;
  isGameOver: boolean;
}

export const initialState:State = {
  playerTiles: Array(7).fill(null),
  // playerTiles: ['Q', null, null, null, null, null, null],
  AITiles: Array(7).fill(null),
  // AITiles: ['Q', null, null, null, null, null, null],
  placedTiles: {
    // '6,7': { ...tileMap['R'], x: 6, y: 7 },
    // '7,7': { ...tileMap['I'], x: 7, y: 7 },
    // '8,7': { ...tileMap['C'], x: 8, y: 7 },
    // '9,7': { ...tileMap['E'], x: 9, y: 7 },
  },
  tempPlacedTiles: {},
  logs: [],
  selectedTileIndex: -1,
  turn: 1,
  isExchangeTilesModalOpen: false,

  // these below variables were previously refs.
  bag: generateBag().slice(0, 15),
  playerTotalScore: 0,
  AITotalScore: 0,
  isGameOver: false,
};

const commonUpdateFunctions = {
  drawTiles: (state:State, player:string, remainingTiles:TilesType) => {
    const newTiles:TilesType = [...remainingTiles];
    for (let i = 0; i < 7; i++) {
      if (state.bag.length && newTiles[i] === null) {
        const tile = state.bag.pop();
        if (tile) {
          newTiles[i] = tile;
        }
      }
    }
    return player === 'player'
      ? { playerTiles: newTiles }
      : { AITiles: newTiles }
  },
  exchangeTiles: (state:State, player:string, selectedIndices:number[]) => {
    // moves a player's selected tiles into bag, then redraws the same amount of tiles.
    if (selectedIndices.length) {
      const remainingTiles = player === 'player' ? [...state.playerTiles] : [...state.AITiles];
      selectedIndices.forEach(index => {
        const letter = player === 'player' ? state.playerTiles[index] : state.AITiles[index];
        if (letter !== null) {
          state.bag.push(letter);
          remainingTiles[index] = null;
        }
      });
      const newLog:Log = {
        turn: state.turn,
        action: 'exchange',
        player
      };
      return {
        logs: [...state.logs, newLog],
        turn: state.turn + 1,
        bag: shuffle(state.bag),
        ...commonUpdateFunctions.drawTiles(state, player, remainingTiles)
      }
    }
    return {};
  },
  pass: (state:State, player:string) => {
    let newPlayerTiles:TilesType = [...state.playerTiles];
    if (player === 'player') {
      // move all temporarily placed player's tiles back into player's hand
      if (Object.keys(state.tempPlacedTiles).length) {
        Object.values(state.tempPlacedTiles).forEach(tile => {
          newPlayerTiles[newPlayerTiles.indexOf(null)] = tile.letter;
        });
      }
    }
    // pass
    const newLog:Log = {
      turn: state.turn,
      action: 'pass',
      player
    };
    return {
      logs: [...state.logs, newLog],
      turn: state.turn + 1,
      tempPlacedTiles: {},
      ...(player === 'player' && { playerTiles: newPlayerTiles }),
    };
  },
  unplaceSelectedTiles: (state:State, coordinates:string[]) => {
    // remove player's placed tile from board and put it back into player's hand
    const newPlayerTiles = [...state.playerTiles];
    const newTempPlacedTiles = { ...state.tempPlacedTiles };
    coordinates.forEach(coordinateString => {
      delete newTempPlacedTiles[coordinateString];
      newPlayerTiles[newPlayerTiles.indexOf(null)] = state.tempPlacedTiles[coordinateString].letter;
    });
    return {
      playerTiles: newPlayerTiles,
      tempPlacedTiles: newTempPlacedTiles
    };
  }
};

export const reducer = (state:State, action:Action): State => {
  switch (action.type) {
    case 'continue_ai_play_word': {
      const { AIMove } = action.payload;
      const remainingTiles:TilesType = [];
      for (let i = 0; i < 7; i++) {
        if (AIMove.AIRemainingTiles[i]) {
          remainingTiles.push(AIMove.AIRemainingTiles[i]);
        } else {
          remainingTiles.push(null);
        }
      }
      const newLog = {
        turn: state.turn,
        action: 'move',
        player: 'AI',
        words: AIMove.words.map(word => ({
          word: word.map(tile => tile.letter).join(''),
          score: generateWordScore(state.placedTiles, word)
        })),
        score: AIMove.score,
        isBingo: Object.keys(AIMove.placedTiles).length === 7
      };

      return {
        ...state,
        ...commonUpdateFunctions.drawTiles(state, 'AI', remainingTiles),
        placedTiles: { ...state.placedTiles, ...AIMove.placedTiles },
        logs: [...state.logs, newLog],
        turn: state.turn + 1,
        AITotalScore: state.AITotalScore + AIMove.score
      };
    }
    case 'continue_ai_pass': {
      return {
        ...state,
        ...(state.bag.length
          // AI turn - exchange
          // if exchanging tiles, the AI will simply exchange all it's tiles.
          // implementing any other logic would be either too complex, or too subjective.
          ? commonUpdateFunctions.exchangeTiles(state, 'AI', [0, 1, 2, 3, 4, 5, 6])
          // AI turn - pass
          : commonUpdateFunctions.pass(state, 'AI')
        )
      };
    }
    case 'player_play_word': {
      const { playerMove } = action.payload;
      const newPlacedTiles = {
        ...state.placedTiles,
        ...playerMove.placedTiles
      };
      const newLog:Log = {
        turn: state.turn,
        action: 'move',
        player: 'player',
        words: playerMove.words.map(word => ({
          word: word.map(tile => tile.letter).join(''),
          score: generateWordScore(state.placedTiles, word)
        })),
        score: playerMove.score,
        isBingo: Object.keys(playerMove.placedTiles).length === 7
      };
      return {
        ...state,
        ...commonUpdateFunctions.drawTiles(state, 'player', state.playerTiles),
        playerTotalScore: state.playerTotalScore + playerMove.score,
        placedTiles: newPlacedTiles,
        tempPlacedTiles: {},
        logs: [...state.logs, newLog],
        turn: state.turn + 1
      }
    }
    case 'draw_tiles_at_start_of_game': {
      return {
        ...state,
        ...commonUpdateFunctions.drawTiles(state, 'player', state.playerTiles),
        ...commonUpdateFunctions.drawTiles(state, 'AI', state.AITiles)
      }
    }
    case 'unplace_selected_tiles': {
      const { coordinates } = action.payload;
      return {
        ...state,
        ...commonUpdateFunctions.unplaceSelectedTiles(state, coordinates)
      };
    }
    case 'place_selected_tile': {
      // place tile from player's hand onto the board
      const { x, y } = action.payload;
      const coordinateString = generateCoordinateString(x, y);
      const letter = state.playerTiles[state.selectedTileIndex];
      if (typeof letter === 'string') {
        const newTempPlacedTiles = {
          ...state.tempPlacedTiles,
          [coordinateString]: { ...tileMap[letter], x, y }
        };
        const newPlayerTiles = [...state.playerTiles];
        newPlayerTiles[state.selectedTileIndex] = null;
        return {
          ...state,
          tempPlacedTiles: newTempPlacedTiles,
          playerTiles: newPlayerTiles,
          selectedTileIndex: -1
        };
      }
      return { ...state };
    }
    case 'open_exchange_tiles_modal': {
      return {
        ...state,
        ...commonUpdateFunctions.unplaceSelectedTiles(state, Object.keys(state.tempPlacedTiles)),
        isExchangeTilesModalOpen: true,
      };
    }
    case 'close_exchange_tiles_modal': {
      const { selectedIndices } = action.payload;
      return {
        ...state,
        ...(selectedIndices.length && commonUpdateFunctions.exchangeTiles(state, 'player', selectedIndices)),
        isExchangeTilesModalOpen: false,
      };
    }
    case 'pass': {
      const { player } = action.payload;
      return {
        ...state,
        ...commonUpdateFunctions.pass(state, player)
      };
    }
    case 'set_selected_tile_index': {
      const { index } = action.payload;
      return {
        ...state,
        selectedTileIndex: state.selectedTileIndex === index ? -1 : index
      };
    }
    case 'set_game_over': {
      const playerTileCount = state.playerTiles.filter(i => i !== null).length
      const AITileCount = state.AITiles.filter(i => i !== null).length
      // game over ondition #1: bag is empty, and one player's hand is empty.
      const condition1 = !state.bag.length && (!playerTileCount || !AITileCount);
      // game over condition #2: 6 turns have passed without any player gaining score.
      // const condition2 = state.logs.slice(state.logs.length - 6).filter(log => !log.score).length === 6;
      const playerScoreBeforeDeductions = state.playerTotalScore;
      const AIScoreBeforeDeductions = state.AITotalScore;
      let playerScorePenalty = 0;
      let AIScorePenalty = 0;
      let winner = '';
      state.playerTiles.forEach(i => {
        if (i !== null) {
          playerScorePenalty += tileMap[i].points;
        }
      });
      state.AITiles.forEach(i => {
        if (i !== null) {
          AIScorePenalty += tileMap[i].points;
        }
      });
      state.playerTotalScore -= playerScorePenalty;
      state.AITotalScore -= AIScorePenalty;
      if (condition1) {
        if (!playerTileCount) {
          state.playerTotalScore += AIScorePenalty;
        } else {
          state.AITotalScore += playerScorePenalty;
        }
      }
      if (state.playerTotalScore > state.AITotalScore) {
        winner = 'player';
      } else if (state.playerTotalScore < state.AITotalScore) {
        winner = 'AI';
      } else if (playerScoreBeforeDeductions > AIScoreBeforeDeductions) {
        winner = 'player';
      } else if (playerScoreBeforeDeductions < AIScoreBeforeDeductions) {
        winner = 'AI';
      }

      const log1:Log = {
        turn: state.turn,
        action: `win_condition_${condition1 ? 1 : 2}`,
        player: !playerTileCount ? 'player' : 'AI'
      };
      const log2:Log = {
        turn: state.turn,
        action: 'score_penalty',
        player: 'player',
        score: playerScorePenalty
      };
      const log3:Log = {
        turn: state.turn,
        action: 'score_penalty',
        player: 'AI',
        score: AIScorePenalty
      };
      const log4_a:Log = {
        turn: state.turn,
        action: 'score_bonus',
        player: 'player',
        score: condition1 && !playerTileCount ? AIScorePenalty : 0
      };
      const log4_b:Log = {
        turn: state.turn,
        action: 'score_bonus',
        player: 'AI',
        score: condition1 && !AITileCount ? playerScorePenalty : 0
      };
      const log4 = condition1 ? (
        !playerTileCount ? log4_a : log4_b
      ) : null;
      const log5:Log = {
        turn: state.turn,
        action: 'winner',
        player: winner
      };

      const newLogs = [...state.logs, log1, log2, log3];
      if (log4 !== null) {
        newLogs.push(log4);
      }
      newLogs.push(log5);

      return {
        ...state,
        isGameOver: true,
        logs: newLogs
      };
    }
    default:
      return state
  }
};
