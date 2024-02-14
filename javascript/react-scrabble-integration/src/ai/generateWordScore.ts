import { board } from '../game/board';
import { generateCoordinateString } from '../game/generateCoordinateString';
import { Tile, PlacedTiles } from '../game/types';

export const generateWordScore = (placedTiles:PlacedTiles, word:Tile[]) => {
  const wordScoreMultipliers:number[] = [];
  let baseWordScore = 0;
  word.forEach(letter => {
    const { x, y, points } = letter;
    const coordinateString = generateCoordinateString(x, y);
    if (placedTiles.hasOwnProperty(coordinateString)) {
      // tile score bonuses are only active for the first word that uses them.
      baseWordScore += points;
    } else {
      baseWordScore += points * board[y][x].letterScoreModifier;
      wordScoreMultipliers.push(board[y][x].wordScoreModifier);
    }
  });
  wordScoreMultipliers.forEach(multiplier => {
    baseWordScore *= multiplier;
  });
  return baseWordScore;
};

export const generateMovesScore = (
  placedTiles:PlacedTiles,
  words:Tile[][],
  numTilesUsed:number
) => ((numTilesUsed === 7 ? 50 : 0) + words
  .map(word => generateWordScore(placedTiles, word))
  .reduce((acc, score) => acc + score)
);
  