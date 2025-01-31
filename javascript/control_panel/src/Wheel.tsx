import './Wheel.scss';
import { useCallback, useEffect, useRef, useState } from 'react';
import { Helmet } from 'react-helmet';
import { fetch_post } from './fetch_functions';
import { WEBSOCKET_EVENT_TYPES } from './enums';

interface WheelItem {
  text: string;
  color: string;
}

const generateRainbowColors = (n: number) => {
  if (n <= 0) return [];
  const colors = [];
  const step = 360 / n; // Divide the hue circle into n equal parts
  for (let i = 0; i < n; i++) {
    const hue = (i * step) % 360; // Calculate hue for each step
    colors.push(`hsl(${hue}, 50%, 55%)`); // color, saturation, lightness
  }
  return colors;
};

const WheelComponent = ({
  items = [],
}:{
  items: WheelItem[],
}) => {
  useEffect(() => {
    const totalSections = items.length; // Number of sections
    const radius = 100; // Radius of the circle
    const svgNS = 'http://www.w3.org/2000/svg';
    const circle = document.querySelector('#sections');
    if (!circle) {
      return;
    }
    for (let i = 0; i < totalSections; i++) {
      const angleStart = (i * 360) / totalSections;
      const angleEnd = ((i + 1) * 360) / totalSections;
      const x1 = 100 + radius * Math.cos((Math.PI * angleStart) / 180);
      const y1 = 100 + radius * Math.sin((Math.PI * angleStart) / 180);
      const x2 = 100 + radius * Math.cos((Math.PI * angleEnd) / 180);
      const y2 = 100 + radius * Math.sin((Math.PI * angleEnd) / 180);
      const largeArcFlag = angleEnd - angleStart > 180 ? 1 : 0;
      const pathData = `
        M 100 100
        L ${x1} ${y1}
        A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}
        Z
      `;
      // Create the path for the section
      const path = document.createElementNS(svgNS, 'path');
      path.setAttribute('d', pathData);
      path.setAttribute('fill', items[i].color);
      circle.appendChild(path);
      // Calculate text position in the middle of the section
      const angleMid = (angleStart + angleEnd) / 2;
      const textX = 100 + (radius / 2) * Math.cos((Math.PI * angleMid) / 180);
      const textY = 100 + (radius / 2) * Math.sin((Math.PI * angleMid) / 180);
      // Create text for the section
      const text = document.createElementNS(svgNS, 'text');
      text.setAttribute('x', textX.toString());
      text.setAttribute('y', textY.toString());
      // Rotate text to align with the section
      const rotateAngle = angleMid; // Rotate to align with the section
      text.setAttribute(
        'transform',
        `rotate(${rotateAngle} ${textX} ${textY})`
      );
      text.textContent = items[i].text;
      circle.appendChild(text);
    }
  }, [items]);

  return (
    <svg
      className='wheel'
      viewBox='0 0 200 200'
      xmlns='http://www.w3.org/2000/svg'
    >
      <g id='sections' />
    </svg>
  );
};

const defaultSpinningStyle = {
  transform: 'rotate(-90deg)',
  transition: 'none'
};
export const Wheel = ({ userInputWheelItems = '' }) => {
  const wsRef = useRef<WebSocket | null>(null);
  const stopSpinningTimeoutRef = useRef<number | NodeJS.Timer>();
  const [items, setItems] = useState<WheelItem[]>([]);
  const itemsRef = useRef<WheelItem[]>([]);
  const [winnerItem, setWinnerItem] = useState<WheelItem | null>(null);
  const [isSpinning, setIsSpinning] = useState(false);
  const [spinningStyle, setSpinningStyle] = useState(defaultSpinningStyle);

  const initiateSpinning = () => {
    if (isSpinning) {
      return;
    }
    // reset the spinning style to default without playing an animation
    setSpinningStyle(defaultSpinningStyle);
    // after reset, use setTimeout(,0) to update the spinning state.
    setTimeout(() => {
      const randomAnimationDuration = 5 + Math.random() * 5; // between 5 and 10 seconds]
      setSpinningStyle({
        transform: `rotate(${(randomAnimationDuration * 360 - 90)}deg)`,
        transition: `transform ${randomAnimationDuration}s cubic-bezier(0.1, 0.8, 0.3, 1)`
      });
      setIsSpinning(true);
      setWinnerItem(null);
      stopSpinningTimeoutRef.current = setTimeout(() => {
        // calculate winner index
        const sliceDegrees = 360 / items.length;
        let newWinnerIndex = 0;
        let counter = 0;
        while (counter > -1 * (randomAnimationDuration * 360)) {
          newWinnerIndex -= 1;
          if (newWinnerIndex < 0) {
            newWinnerIndex = items.length - 1;
          }
          counter -= sliceDegrees;
        }
        setWinnerItem(itemsRef.current[newWinnerIndex]);
        setIsSpinning(false);
      }, randomAnimationDuration * 1000);
    }, 0);
  };

  const handleClickTriangle = () => {
    const inputItemsCSV = prompt('Input wheel items CSV: ') || '';
    const colors = generateRainbowColors(inputItemsCSV.split(',').length);
    const newItems = inputItemsCSV.split(',').map((item, index) => ({
      text: item,
      color: colors[index]
    }));
    setItems(newItems);
    itemsRef.current = newItems;
  };

  useEffect(() => {
    // const items = ['Zany', 'Bamboozle', 'Snazzy', 'Whimsy', 'Kerfuffle', 'Giggle', 'Hullabaloo', 'Quizzical'];
    // const colors = generateRainbowColors(items.length);
    // const newItems = items.map((item, index) => ({
    //   text: item,
    //   color: colors[index]
    // }));
    // setItems(newItems);
    // itemsRef.current = newItems;
    if (wsRef.current) {
      wsRef.current.close();
    }
    const ws = new WebSocket('ws://localhost:4000');
    wsRef.current = ws;
    ws.addEventListener('open', () => {
      console.log('Connected to WebSocket server!');
    });
    ws.addEventListener('message', (_data) => {
      const data = JSON.parse(_data.data);
      if (data.type === WEBSOCKET_EVENT_TYPES['LUNA_WHEEL']) {
        if (data.payload) {
          const items:string[] = data.payload.split(',');
          const colors = generateRainbowColors(items.length);
          const newItems = items.map((item, index) => ({
            text: item,
            color: colors[index]
          }));
          setItems(newItems);
          itemsRef.current = newItems;
          setTimeout(() => initiateSpinning(), 2000);
        }
      }
    });

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      clearTimeout(stopSpinningTimeoutRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className='wheel_container'>
      <div
        className='wheel_rotation_container'
        style={spinningStyle}
      >
        <WheelComponent items={items} />
      </div>
      <div className='wheel_border' />
      <div className='wheel_center' onClick={initiateSpinning}>
        {isSpinning ? <div className='lunaspin-gif' /> : <div className='lunaspin-still' />}
      </div>
      <div className='wheel_triangle_container' onClick={handleClickTriangle}>
        <div className='wheel_triangle' />
      </div>
      {winnerItem && (
        <div className='wheel_winner_text' style={{ color: winnerItem.color }}>
          <u>{winnerItem.text}</u> WINS!!!
        </div>
      )}
    </div>
  );
};

export const WheelPage = () => {
  return (
    <div className='wheel_page'>
      <Helmet><title>Luna Wheel</title></Helmet>

      <Wheel />
    </div>
  );
};
