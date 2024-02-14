import { generateCoordinateString } from './generateCoordinateString';
import { Board, Square } from './types';
import { range } from 'lodash';

const tripleWordScoreCoordinates:string[] = ['0,0', '7,0', '14,0', '14,7', '0,7', '0,14', '7,14', '14,14'];
const doubleWordScoreCoordinates:string[] = ['1,1', '2,2', '3,3', '4,4', '13,1', '12,2', '11,3', '10,4', '13,13', '12,12', '11,11', '10,10', '1,13', '2,12', '3,11', '4,10'];
const doubleLetterScoreCoordinates:string[] = ['3,0', '0,3', '11,0', '14,3', '14,11', '11,14', '3,14', '0,11', '3,7', '2,6', '2,8', '6,2', '7,3', '8,2', '7,11', '6,12', '8,12', '11,7', '12,6', '12,8', '6,6', '8,6', '8,8', '6,8'];
const tripleLetterScoreCoordinates:string[] = ['1,5', '1,9', '5,1', '9,1', '13,5', '13,9', '5,13', '9,13', '5,5', '9,5', '9,9', '5,9'];

export const board:Board = range(0, 15).map(y => (
  range(0, 15).map(x => {
    const coordinateString = generateCoordinateString(x, y);
    const square:Square = {
      text: '',
      letterScoreModifier: 1,
      wordScoreModifier: 1,
      x,
      y,
      color: 'transparent'
    };

    if (tripleWordScoreCoordinates.includes(coordinateString)) {
      square.text = 'TRIPLE WORD SCORE';
      square.wordScoreModifier = 3;
      square.color = 'salmon';
    } else if (doubleWordScoreCoordinates.includes(coordinateString)) {
      square.text = 'DOUBLE WORD SCORE';
      square.wordScoreModifier = 2;
      square.color = 'pink';
    } else if (doubleLetterScoreCoordinates.includes(coordinateString)) {
      square.text = 'DOUBLE LETTER SCORE';
      square.letterScoreModifier = 2;
      square.color = 'powderblue';
    } else if (tripleLetterScoreCoordinates.includes(coordinateString)) {
      square.text = 'TRIPLE LETTER SCORE';
      square.letterScoreModifier = 3;
      square.color = 'dodgerblue';
    } else if (coordinateString === generateCoordinateString(7, 7)) {
      // the middle tile counts as a "double word score", according to official scrabble rules.
      square.wordScoreModifier = 2;
      square.color = 'pink';
    }
    
    return square;
  })
));
