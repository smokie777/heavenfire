import './LetterDistribution.scss';
import { tileMap } from '../game/tiles';
import { PlacedTiles } from '../game/types';
import { FlexContainer } from './FlexContainer';

export const LetterDistribution = ({ placedTiles }:{ placedTiles:PlacedTiles }) => {
  const placedTileCounts:{[key:string]:number} = {};
  Object.values(placedTiles).forEach(tile => {
    if (placedTileCounts.hasOwnProperty(tile.letter)) {
      placedTileCounts[tile.letter]++;
    } else {
      placedTileCounts[tile.letter] = 1;
    }
  });

  return (
    <FlexContainer className='letter_distribution' justifyContent='flex-end'>
      <FlexContainer className='letter_distribution_container' flexDirection='column' alignItems='center'>
        <div>LETTER</div>
        <div>DISTRIBUTION</div>
        <br />
        <FlexContainer className='letter_counts'>
          {[0, -1, 13].map(offset => offset === -1 ? ( // the "-1" is a placeholder div
            <div key={offset} style={{ width: '5px' }} />
          ) : (
            <FlexContainer
              key={offset}
              className='letter_distribution_col'
              flexDirection='column'
              alignItems={offset ? 'flex-end' : 'flex-start'}
            >
              {Object.values(tileMap).slice(0 + offset, 13 + offset).map((tile, index) => (
                <FlexContainer
                  key={index}
                  justifyContent='space-between'
                  className='letter_distribution_text'
                >
                  <div>{tile.letter}-</div>
                  <div>{placedTileCounts[tile.letter] || 0}/{tileMap[tile.letter].count}</div>
                </FlexContainer>
              ))}
            </FlexContainer>
          ))}
        </FlexContainer>
        <div>BLANK- {placedTileCounts._ || 0}/{tileMap._.count}</div>
      </FlexContainer>
    </FlexContainer>
  );
};
