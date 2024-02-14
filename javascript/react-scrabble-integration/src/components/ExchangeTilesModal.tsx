import './ExchangeTilesModal.scss';
import { useState } from 'react';
import { FlexContainer } from './FlexContainer';
import { Tiles as TilesType } from '../game/types';
import { Tiles } from './Tiles';
import { Spacer } from './Spacer';
import { Button } from './Button';

export const ExchangeTilesModal = ({
  tiles,
  onExchangeClick,
  onCancelClick
}:{
  tiles:TilesType,
  onExchangeClick:Function,
  onCancelClick:Function
}) => {
  const [selectedIndices, setSelectedIndices] = useState<number[]>([]);

  const selectTile = (index:number) => {
    const newSelectedIndices = [...selectedIndices];
    if (selectedIndices.indexOf(index) === -1) {
      newSelectedIndices.push(index);
    } else {
      newSelectedIndices.splice(newSelectedIndices.indexOf(index), 1);
    }
    setSelectedIndices(newSelectedIndices);
  };

  return (
    <FlexContainer className='modal' flexDirection='column' justifyContent='center' alignItems='center'>
      <div className='subtitle'>Select tiles to exchange:</div>
      <Spacer height={20} />
      <Tiles tiles={tiles} tileOnClick={selectTile} selectedTileIndices={selectedIndices} />
      <Spacer height={20} />
      <Button type='green' onClick={() => onExchangeClick(selectedIndices)} isDisabled={!selectedIndices.length}>
        Exchange
      </Button>
      <Spacer height={10} />
      <Button type='red' onClick={onCancelClick}>
        Cancel
      </Button>
    </FlexContainer>
  );
};
