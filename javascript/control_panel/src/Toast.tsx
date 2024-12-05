import { Spacer } from './Spacer';
import './Toast.scss';

const resetToastAnimation = () => {
  const el = document.querySelector('.toast_animation');
  if (el instanceof HTMLElement) {
    el.classList.remove('toast_animation');
    void el.offsetWidth;
    el.classList.add('toast_animation');
  }
};

export const Toast = ({
  toast = '',
  rerenderIdenticalToastFlipper = false
}:{
  toast: string,
  rerenderIdenticalToastFlipper: boolean
}) => {
  resetToastAnimation();

  return toast ? (
    <div className='toast toast_animation'>
      <Spacer width={30} />
      <div className='toast_text'>{toast}</div>
      <Spacer width={30} />
    </div>
  ) : null;
};
