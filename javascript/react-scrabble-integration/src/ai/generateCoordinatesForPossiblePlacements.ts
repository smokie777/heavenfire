import { generateCoordinateString } from '../game/generateCoordinateString';
import { PlacedTiles } from '../game/types';
import { directionMatrix } from './DirectionMatrix';

export const generateCoordinatesForPossiblePlacements = (
  placedTiles:PlacedTiles, // map of all tiles on the board
  tempPlacedTiles:PlacedTiles, // map of all temp tile placements for move calculation
) => {
  // generates an array of all valid stringCoordinates to place one letter, given board states  
  const coordinates:{x:number,y:number}[] = [];
  const placedTilesArr = Object.values(placedTiles);
  const tempPlacedTilesArr = Object.values(tempPlacedTiles);
  const numLettersPlaced = tempPlacedTilesArr.length;

  if (!placedTilesArr.length && !numLettersPlaced) {
    // the first word of the game must be placed over the center square.
    return [{ x: 7, y: 7 }];
  } else if (!numLettersPlaced) {
    // the first letter can be placed anywhere adjacent to a pre-existing placed letter.
    for (let i = 0; i < placedTilesArr.length; i++) {
      const { x, y } = placedTilesArr[i];
      for (let j = 0; j < directionMatrix.length; j++) {
        const xMod = directionMatrix[j][0];
        const yMod = directionMatrix[j][1];
        const coordinateString = generateCoordinateString(x + xMod, y + yMod);
        if (
          x + xMod >= 0 && x + xMod <= 14
          && y + yMod >= 0 && y + yMod <= 14
          && !placedTiles.hasOwnProperty(coordinateString)
        ) {
          coordinates.push({ x: x + xMod, y: y + yMod });
        }
      }
    }
  } else {
    const possibleDirections = numLettersPlaced === 1
      // the second letter must only be placed on the same row or column as the first letter.
      ? directionMatrix
      // the third and onwards letters must only be placed on the same row or column as the first two letters were on.
      : (
        tempPlacedTilesArr[0].x === tempPlacedTilesArr[1].x
          ? directionMatrix.slice(0, 2)
          : directionMatrix.slice(2)
      )
    ;

    possibleDirectionsLoop: for (let i = 0; i < possibleDirections.length; i++) {
      // from first letter, travel in all directions until either an empty square or the edge of the board is found.
      const xMod = possibleDirections[i][0];
      const yMod = possibleDirections[i][1];
      let counter = 1;
      const { x, y } = tempPlacedTilesArr[0];
      while (true) {
        const coordinateString = generateCoordinateString(x + xMod * counter, y + yMod * counter);
        if (
          x + xMod * counter < 0 || x + xMod * counter > 14
          || y + yMod * counter < 0 || y + yMod * counter > 14
        ) {
        // if out of bounds, stop searching in that direction.
          continue possibleDirectionsLoop;
        } else if (
          !placedTiles.hasOwnProperty(coordinateString)
          && !tempPlacedTiles.hasOwnProperty(coordinateString)
        ) {
          // if empty square is found, add coordinates, then proceed to the next direction.
          coordinates.push({ x: x + xMod * counter, y: y + yMod * counter });
          continue possibleDirectionsLoop;
        } else {
          // if non-empty, in-bounds square is found, keep searching in that direction.
          counter++;
        }
      }
    }
  }

  return coordinates;
};
