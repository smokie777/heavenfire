import './Button.scss';
import { noop } from 'lodash';

export const Button = ({
  type,
  isDisabled = false,
  onClick = noop,
  children = null
}:{
  type:string,
  isDisabled?:Boolean,
  onClick?:Function,
  children?:any
}) => (
  <div
    className={`button ${type} ${isDisabled ? 'disabled' : ''}`}
    onClick={isDisabled ? noop : () => onClick()}
  >
    {children}
  </div>
);
