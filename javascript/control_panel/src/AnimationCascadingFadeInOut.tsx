import './AnimationCascadingFadeInOut.scss';
import { ReactNode } from 'react';

export const AnimationCascadingFadeInOut = ({
  items = [],
  className = ''
}:{
  items: ReactNode[];
  className: string;
}) => {
  return (
    <div className={`animation_cascading_fade_in_out ${className}`}>
      {items.map((item, index) => (
        <div
          key={index}
          className={`animation_item animation_item--${index}`}
        >
          {item}
        </div>
      ))}
    </div>
  )
};
