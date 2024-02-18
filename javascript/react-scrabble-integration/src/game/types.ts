export interface Log {
  turn:number,
  action:string,
  player:string,
  words?:{
    word:string,
    score:number
  }[],
  score?:number,
  isBingo?:Boolean
}

export interface Tile {
  letter:string,
  points:number,
  count:number,
  x:number,
  y:number,
}
export interface PlacedTiles {
  [key:string]:Tile
};
export type Tiles = (string|null)[];

export interface Square {
  text:string;
  letterScoreModifier:number;
  wordScoreModifier:number;
  x:number;
  y:number;
  color:string;
}
export type SquareRow = Square[];
export type Board = SquareRow[];
export interface SquareCoordinateMap {
  [key:string]:Square
}

export interface Move {
  placedTiles:PlacedTiles, // board state
  words:Tile[][], // all words created by the move
  score:number, // total score of move
  AIRemainingTiles:string[] // what tiles AI has left after the move,
}
export type Moves = Move[]

export type ScrabbleChatCommand =
  | {
    type: 'play',
    username: string,
    letters: string,
    startTileX: number,
    startTileY: number,
    direction: 'horizontal' | 'vertical'
  }
  | { type: 'exchange', username: string, letters: string }
  | { type: 'pass', username: string };
export type ScrabbleChatCommands = ScrabbleChatCommand[];
