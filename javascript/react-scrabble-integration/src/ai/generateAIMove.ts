import { tileMap } from '../game/tiles';
import { uniq } from 'lodash';
import { PlacedTiles, Tile, Moves } from '../game/types';
import { twl06 } from '../game/twl06';
import { twl06InvalidSequences } from '../game/twl06InvalidSequences';
import { keyBy } from 'lodash';
import { generateMovesScore } from './generateWordScore';
import { generateCoordinatesForPossiblePlacements } from './generateCoordinatesForPossiblePlacements';
import { directionMatrix } from './DirectionMatrix';
import { generateCoordinateString } from '../game/generateCoordinateString';
import { forEverySequencePermutation } from './forEverySequencePermutation';

// limits AI processing time per turn.
// removing this limit will allow the AI to calculate the best possible move every time,
// but it could take upwards of 10 seconds if the board/tile states are very complex.
// if processing time is limited, the AI will calculate the best move it could find in the given time.
const maxAITurnTime = 10000; // ms

const generatePlacementCacheId = (placements:Tile[]) => {
  const placementCacheIdArr:string[] = placements.map(i => `${i.x},${i.y},${i.letter}`);
  placementCacheIdArr.sort();
  return placementCacheIdArr.join('_');
};

// generateAIMoves uses DFS recursion, with "depth" referring to the length of the word being generated.
const generateAIMoves = ( 
  placedTiles:PlacedTiles, // map of all tiles on the board
  tiles:string[], // array of all tiles in ai's hand
  tempPlacedTiles:PlacedTiles, // map of all temp tile placements for move calculation
  placementCache:{[key:string]:boolean}, // cache of all already-explored placements to prevent dupes
  horizontalSequences:Tile[][], // all horizontal sequences generated so far
  verticalSequences:Tile[][], // all vertical sequences generated so far
  moves:Moves, // array of all possible moves. populated by this function.
  timeStart:number, // time first function call started in ms
  perfMetrics:{[key:string]:any} // performance metrics for development purposes only
) => {
  perfMetrics.timesGenerateAIMovesCalled++;

  const tilesDeduped:string[] = uniq(tiles);
  const coordinates = generateCoordinatesForPossiblePlacements(placedTiles, tempPlacedTiles);

  // iterate through all deduped tiles, and process all possible horizontal and vertical sequence
  // created by placing that tile in a valid coordinate
  for (let i = 0; i < tilesDeduped.length; i++) {
    coordinatesLoop: for (let j = 0; j < coordinates.length; j++) {
      perfMetrics.placementsTotalAttempted++;
      const { x, y } = coordinates[j];
      const placement:Tile = { ...tileMap[tilesDeduped[i]], x, y };
      const newTempPlacedTiles = { ...tempPlacedTiles };
      newTempPlacedTiles[generateCoordinateString(x, y)] = placement;
      // cache a unique id based on placement coordinates and letter to prevent duplicate iterations
      // such as iterating on 5,5 -> 5,6, and also 5,6 -> 5,5.
      const placementCacheId = generatePlacementCacheId(Object.values(newTempPlacedTiles));
      if (placementCache.hasOwnProperty(placementCacheId)) {
        perfMetrics.placementsSkippedDueToCaching++;
        continue; // proceed to the next coordinate for tile
      }
      placementCache[placementCacheId] = true;

      const horizontalSequence = [placement];
      const verticalSequence = [placement];
      for (let k = 0; k < directionMatrix.length; k++) {
        // find the horizontal and vertical sequence containing target square.
        const xMod = directionMatrix[k][0];
        const yMod = directionMatrix[k][1];
        let counter = 1;
        while (true) {
          const coordinateString = generateCoordinateString(x + xMod * counter, y + yMod * counter);
          const tile:Tile|null = placedTiles[coordinateString] || newTempPlacedTiles[coordinateString] || null;
          if (tile) {
            if (yMod === 1) { // traveling down
              verticalSequence.push(tile);
            } else if (yMod === -1) { // traveling up
              verticalSequence.unshift(tile);
            } else if (xMod === 1) { // traveling right
              horizontalSequence.push(tile);
            } else if (xMod === -1) { // traveling left
              horizontalSequence.unshift(tile);
            }
            counter++;
          } else { // if an empty tile (or edge of board) has been found, stop traveling in that direction.
            break; // continue with the next direction.
          }
        }
      }

      // generate array of all sequences as of playing the placement.
      // placing a letter after the first will change a sequence that was previously formed.
      // so, depending on whether the placement was horizontal or vertical, respective previous sequences need to be overwritten.
      let newHorizontalSequences = [...horizontalSequences];
      let newVerticalSequences = [...verticalSequences];
      if (Object.keys(tempPlacedTiles).length > 0) {
        if (Object.values(tempPlacedTiles)[0].x === placement.x) {
          // placement is vertical
          newVerticalSequences = [];
        } else {
          // placement is horizontal
          newHorizontalSequences = [];
        }
      }
      if (horizontalSequence.length > 1) {
        newHorizontalSequences.push(horizontalSequence);
      }
      if (verticalSequence.length > 1) {
        newVerticalSequences.push(verticalSequence);
      }
      const combinedNewSequences = [...newHorizontalSequences, ...newVerticalSequences];

      // iterate through all blank-permutations of all sequences, and check sequence validity.
      let areAllSequencesValidWords = true;
      for (let k = 0; k < combinedNewSequences.length; k++) {
        let isSequenceInvalid = true; // a sequence is invalid if it is not present in any twl06 word.
        let isSequenceAValidWord = false; // a sequence is a valid word if it is in twl06.
        const cb = (permutation:string) => {
          // if any one permutation is a valid word, the sequence is also a valid word.
          if (!twl06InvalidSequences.hasOwnProperty(permutation)) {
            isSequenceInvalid = false;
          }
          if (twl06.hasOwnProperty(permutation)) {
            isSequenceAValidWord = true;
          }
        };
        forEverySequencePermutation(combinedNewSequences[k].map(tile => tile.letter).join(''), cb);
        if (isSequenceInvalid) {
          // if at least one sequence is invalid, stop processing this placement.
          // ("placement" here refers to a combo of a tile and a coordinate.)
          perfMetrics.placementsTerminatedDueToInvalidSequence++;
          continue coordinatesLoop;
        }
        if (!isSequenceAValidWord) {
          areAllSequencesValidWords = false;
        }
      }

      // if all sequences are valid scrabble words, record a possible "move".
      const newTiles = [...tiles];
      newTiles.splice(newTiles.indexOf(placement.letter), 1);
      if (combinedNewSequences.length && areAllSequencesValidWords) {
        moves.push({
          placedTiles: newTempPlacedTiles,
          words: combinedNewSequences,
          score: generateMovesScore(
            placedTiles,
            combinedNewSequences,
            Object.keys(newTempPlacedTiles).length
          ),
          AIRemainingTiles: newTiles,
        });
      }

      // add the next letter.
      perfMetrics.placementsFullyProcessed++;
      if (newTiles.length && Date.now() - timeStart < maxAITurnTime) {
        generateAIMoves(
          placedTiles,
          newTiles,
          newTempPlacedTiles,
          placementCache,
          newHorizontalSequences,
          newVerticalSequences,
          moves,
          timeStart,
          perfMetrics
        );
      }
    }
  }
};

export const generateAIMove = (
  placedTiles:PlacedTiles, // map of all tiles on the board
  tiles:string[], // array of all tiles in ai's hand
) => {
  const timeStart = Date.now();

  const moves:Moves = [];
  const perfMetrics:{[key:string]:any} = {
    placementsTotalAttempted: 0,
    placementsSkippedDueToCaching: 0,
    placementsTerminatedDueToInvalidSequence: 0,
    placementsFullyProcessed: 0,
    timesGenerateAIMovesCalled: 0
  };

  generateAIMoves(placedTiles, tiles, {}, {}, [], [], moves, timeStart, perfMetrics);

  moves.sort((a, b) => b.score - a.score);

  const timeTaken = Date.now() - timeStart;

  const fancyDisplayResult = moves
    .map((i, index) => ({
      ...i,
      stringifiedWords: `${JSON.stringify(i.words.map(j => j.map(k => k.letter).join('')))}_${index}`
    })
  );
  console.log(`found ${moves.length} possible moves in ${timeTaken}ms`);
  if (moves.length) {
    console.log(`the best move is "${fancyDisplayResult[0].stringifiedWords}", scoring ${fancyDisplayResult[0].score}`);
  }
  console.log(`perfMetrics: `, perfMetrics)
  console.log(`all possible moves here:`, keyBy(fancyDisplayResult, 'stringifiedWords'));
  console.log('-----');

  // return the top scoring move. this is not optimal from a competitive scrabble play point of view,
  // but adding any additional heuristics would be quite difficult and out of scope for my coding ability.
  return moves[0];
};
