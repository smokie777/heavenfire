import { tileMap } from '../game/tiles';
import { Tiles as TilesType } from '../game/types';
import { Tile } from './Tile';
import { noop } from 'lodash';

export const Tiles = ({
  tiles,
  tileOnClick = noop,
  selectedTileIndices = [],
  areTilesHidden = false
}:{
  tiles:TilesType,
  selectedTileIndices?:number[],
  tileOnClick?:Function,
  areTilesHidden?:Boolean
}) => (
  <div className='tiles'>
    {tiles.map((tile, index) => tile === null ? (
      <div key={index} className='tile hidden' />
    ) : (
      <Tile
        key={index}
        letter={areTilesHidden ? '_' : tileMap[tile].letter}
        points={tileMap[tile].points}
        index={index}
        onClick={() => tileOnClick(index)}
        isSelected={selectedTileIndices.includes(index)}
      />
    ))}
  </div>
);
