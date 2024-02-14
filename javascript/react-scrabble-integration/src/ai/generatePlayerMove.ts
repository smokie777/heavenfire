import { generateCoordinateString } from '../game/generateCoordinateString';
import { twl06 } from '../game/twl06';
import { PlacedTiles, Moves, Tile } from '../game/types';
import { directionMatrix } from './DirectionMatrix';
import { forEverySequencePermutation } from './forEverySequencePermutation';
import { generateMovesScore } from './generateWordScore';

const areAllNumsTheSameValue = (arr:any[]) => (
  arr.length ? arr.filter(i => i === arr[0]).length === arr.length : true
);

export const generatePlayerMove = (
  placedTiles:PlacedTiles, // map of all tiles on the board
  tempPlacedTiles:PlacedTiles, // map of all letters player played
) => {
  const moves:Moves = [];
  const sequences:Tile[][] = [];
  const placements = Object.values(tempPlacedTiles);
  
  // validate if placement order is legal (all tiles must be placed on the same line)
  if (
    !placements.length
    || (placements.length === 1 && !Object.keys(placedTiles).length)
    || (!areAllNumsTheSameValue(placements.map(i => i.x)) && !areAllNumsTheSameValue(placements.map(i => i.y)))
  ) {
    return [];
  }
  // validate if placement location is legal (at least one placed tile must be adjacent to a pre-placed tile)
  for (let i = 0; i < placements.length; i++) {
    let isAtLeastOnePlacementAdjacentToPrePlacedTile = false;
    // if playing the first move, it's valid if it is played over the center tile.
    if (!Object.keys(placedTiles).length && placements[i].x === 7 && placements[i].y === 7) {
      break;
    }
    for (let j = 0; j < directionMatrix.length; j++) {
      const coordinateString = generateCoordinateString(
        placements[i].x + directionMatrix[j][0],
        placements[i].y + directionMatrix[j][1]
      );
      if (placedTiles.hasOwnProperty(coordinateString)) {
        isAtLeastOnePlacementAdjacentToPrePlacedTile = true;
        break;
      }
    }
    if (isAtLeastOnePlacementAdjacentToPrePlacedTile) {
      break;
    }
    if (i === placements.length - 1) {
      return [];
    }
  }

  // direction of the placements.
  const direction = placements.length > 1 && placements[0].x === placements[placements.length - 1].x
    ? 'vertical'
    : 'horizontal';

  // generate all sequences created by the move
  const crosswordDirectionMatrix = direction === 'vertical'
    ? directionMatrix.slice(2)
    : directionMatrix.slice(0, 2);
  const mainWordDirectionMatrix = direction === 'vertical'
    ? directionMatrix.slice(0, 2)
    : directionMatrix.slice(2);
  [
    ...placements, // this is used to generate "crosswords".
    placements[0] // this last "placement" is used to generate the "main word".
  ].forEach((placement, index) => {
    const sequence = [placement];
    (index === placements.length ? mainWordDirectionMatrix : crosswordDirectionMatrix).forEach(i => {
      // find the horizontal or vertical sequence containing target square.
      let counter = 1;
      while (true) {
        const coordinateString = generateCoordinateString(placement.x + i[0] * counter, placement.y + i[1] * counter);
        const tile:Tile|null = placedTiles[coordinateString] || tempPlacedTiles[coordinateString] || null;
        if (tile) {
          if (i[1] === 1) { // traveling down
            sequence.push(tile);
          } else if (i[1] === -1) { // traveling up
            sequence.unshift(tile);
          } else if (i[0] === 1) { // traveling right
            sequence.push(tile);
          } else if (i[0] === -1) { // traveling left
            sequence.unshift(tile);
          }
          counter++;
        } else { // if an empty tile (or edge of board) has been found, stop traveling in that direction.
          return; // return out of forEach() and continue with the next direction.
        }
      }
    });
    if (sequence.length > 1) {
      sequences.push(sequence);
    }
  });

  // iterate through all blank-permutations of all sequences, and check sequence validity.
  let areAllSequencesValidWords = true;
  for (let i = 0; i < sequences.length; i++) {
    let isSequenceAValidWord = false; // a sequence is a valid word if it is in twl06.
    const cb = (permutation:string) => {
      if (twl06.hasOwnProperty(permutation)) {
        isSequenceAValidWord = true;
      }
    };
    forEverySequencePermutation(sequences[i].map(tile => tile.letter).join(''), cb);
    if (!isSequenceAValidWord) {
      areAllSequencesValidWords = false;
    }
  }

  // if all sequences are valid scrabble words, record a "move".
  if (areAllSequencesValidWords) {
    moves.push({
      placedTiles: tempPlacedTiles,
      words: sequences,
      score: generateMovesScore(
        placedTiles,
        sequences,
        Object.keys(tempPlacedTiles).length
      ),
      AIRemainingTiles: []
    });
  }

  return moves;
};
