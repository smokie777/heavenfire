import { useState, useRef, useCallback, useEffect } from 'react';
import { Spacer } from './Spacer';
import { fetch_post } from './fetch_functions';

// make channel point redeem for luna saying "im gonna punch you in the face"

export const App = () => {
  const [textBoxInput, setTextBoxInput] = useState('')

  const lunaAnswerTextBox = () => {
    fetch_post('/receive_prompt', {
      prompt: textBoxInput,
      priority: 5
    });
    setTextBoxInput('');
  };

  // const lunaReadTextBox = () => {
  //   fetch_post('/receive_prompt', {
  //     prompt: textBoxInput,
  //     priority: 2
  //   });
  //   setTextBoxInput('');
  // };

  return (
    <div className='app_container'>
      <div className='app'>
        <textarea
          value={textBoxInput}
          onChange={(e) => setTextBoxInput(e.target.value)}
        />
        <Spacer height={10} />
        <div className='textbox_buttons'>
          <button onClick={lunaAnswerTextBox}>Answer</button>
          <Spacer width={20} />
          {/* <button onClick={() => lunaReadTextBox(false)}>Read</button>
          <Spacer width={20} />
          <button onClick={() => lunaReadTextBox(true)}>Generate audio file</button>
          <Spacer width={20} /> */}
          {/* <button onClick={lunaCancelSpeech}>Cancel speech</button> */}
        </div>
      </div>
    </div>
  );
};
