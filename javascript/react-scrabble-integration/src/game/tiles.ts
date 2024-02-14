import { Tile } from './types';
import { shuffle } from 'lodash';

interface TileMap {
  [key:string]:Tile
};
export const tileMap:TileMap = {
  A: { letter: 'A', points: 1, count: 9, x: -1, y: -1 },
  B: { letter: 'B', points: 3, count: 2, x: -1, y: -1 },
  C: { letter: 'C', points: 3, count: 2, x: -1, y: -1 },
  D: { letter: 'D', points: 2, count: 4, x: -1, y: -1 },
  E: { letter: 'E', points: 1, count: 12, x: -1, y: -1 },
  F: { letter: 'F', points: 4, count: 2, x: -1, y: -1 },
  G: { letter: 'G', points: 2, count: 3, x: -1, y: -1 },
  H: { letter: 'H', points: 4, count: 2, x: -1, y: -1 },
  I: { letter: 'I', points: 1, count: 9, x: -1, y: -1 },
  J: { letter: 'J', points: 8, count: 1, x: -1, y: -1 },
  K: { letter: 'K', points: 5, count: 1, x: -1, y: -1 },
  L: { letter: 'L', points: 1, count: 4, x: -1, y: -1 },
  M: { letter: 'M', points: 3, count: 2, x: -1, y: -1 },
  N: { letter: 'N', points: 1, count: 6, x: -1, y: -1 },
  O: { letter: 'O', points: 1, count: 8, x: -1, y: -1 },
  P: { letter: 'P', points: 3, count: 2, x: -1, y: -1 },
  Q: { letter: 'Q', points: 10, count: 1, x: -1, y: -1 },
  R: { letter: 'R', points: 1, count: 6, x: -1, y: -1 },
  S: { letter: 'S', points: 1, count: 4, x: -1, y: -1 },
  T: { letter: 'T', points: 1, count: 6, x: -1, y: -1 },
  U: { letter: 'U', points: 1, count: 4, x: -1, y: -1 },
  V: { letter: 'V', points: 4, count: 2, x: -1, y: -1 },
  W: { letter: 'W', points: 4, count: 2, x: -1, y: -1 },
  X: { letter: 'X', points: 8, count: 1, x: -1, y: -1 },
  Y: { letter: 'Y', points: 4, count: 2, x: -1, y: -1 },
  Z: { letter: 'Z', points: 10, count: 1, x: -1, y: -1 },
  _: { letter: '_', points: 0, count: 2, x: -1, y: -1 }
};

export const generateBag = () => {
  const bag:string[] = [];

  Object.values(tileMap).forEach(tile => {
    for (let i = 0; i < tile.count; i++) {
      bag.push(tile.letter);
    }
  });

  return shuffle(bag);
};

/*
English-language editions of Scrabble contain 100 letter tiles, in the following distribution:

2 blank tiles (scoring 0 points)
1 point: E ×12, A ×9, I ×9, O ×8, N ×6, R ×6, T ×6, L ×4, S ×4, U ×4
2 points: D ×4, G ×3
3 points: B ×2, C ×2, M ×2, P ×2
4 points: F ×2, H ×2, V ×2, W ×2, Y ×2
5 points: K ×1
8 points: J ×1, X ×1
10 points: Q ×1, Z ×1
*/
