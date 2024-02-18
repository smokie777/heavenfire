import { generateCoordinateString } from '../game/generateCoordinateString';
import { PlacedTiles, ScrabbleChatCommand } from '../game/types';
import { tileMap } from '../game/tiles';

// this function generates tempPlacedTiles for generatePlayerMove.
export const generateTempPlacedTilesForChatCommandPlay = (
  command:ScrabbleChatCommand,
  placedTiles:PlacedTiles, // map of all tiles on the board
) => {
  if (command.type === 'play') {
    let tempPlacedTiles:PlacedTiles = {};
    
    let letters = command.letters.split(''); // cast to array for .shift()
    let x = command.startTileX;
    let y = command.startTileY;
    let direction = command.direction;
    // from start tile, iterate across tiles in placedTiles in command.direction
    while (letters.length) {
      // if board out-of-bounds is reached, return {}
      if (x > 15 || y > 15) {
        return {};
      }

      const coordinateString = generateCoordinateString(x, y);
      
      if (!placedTiles.hasOwnProperty(coordinateString)) {
        // if tile does not exist in placedTiles,
        // remove 1 letter from command.letters, and...
        const letter = letters.shift();
        // add that letter to tempPlacedTiles
        if (letter) {
          tempPlacedTiles[coordinateString] = { ...tileMap[letter], x, y };
        }
      } else if (placedTiles[coordinateString].letter === letters[0]) {
        // if tile exists in placedTiles, and has same letter, remove it from command.letters, and continue
        letters.shift();
      } else {
        // if tile exists in placedTiles, and is different letter, it's an invalid command.
        return {};
      }

      // continue
      if (direction === 'horizontal') {
        x++;
      } else {
        y++;
      }
    }
    // if letters is [], return tempPlacedTiles
    return tempPlacedTiles;
  }
  return {};
};
