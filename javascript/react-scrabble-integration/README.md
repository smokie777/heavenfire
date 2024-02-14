## React Scrabble
Hello! Welcome to React Scrabble, a personal project I'm developing. As of now, the game is fully functioning and playable, although the UI is still in somewhat of a rudimentary state 😅.
- React Scrabble uses React, TypeScript, and SCSS to create a fully-functioning Scrabble clone.
- Functionality includes:
  - Feature-complete game functionality, with all [official rules](https://www.hasbro.com/common/instruct/Scrabble_(2003).pdf) for gameplay & scoring implemented
  - An AI that you can play against WHICH WILL PROBABLY BEAT YOU and make you question your sanity
  - Ability to look up played words on the [Free Dictionary API](https://dictionaryapi.dev/)
  - The game uses the [TWL06 Scrabble Word List](https://www.wordgamedictionary.com/twl06/) as the "dictionary".

![image](https://github.com/smokie777/react-scrabble/assets/31945139/d4acfc9b-0e93-4394-9f25-7bc37977b8bd)

## AI Notes
Developing the AI for this project was a fairly interesting and complex process.
- The AI that I created uses DFS recursion to iterate through all possible placement sequences that result in valid Scrabble words, and then returns the highest scoring sequence. The depth of the recursion is equal to the length of the sequence being evaluated.
- I tried my best to make it as fast as possible, by implementing optimizations such as:
  - Caching sequence iterations by sorted letter-coordinate unique ID strings (it's a bit complicated, but saves a lot of iterations)
  - Pre-generating a dictionary of 400k 2-4 letter invalid sequences that do not occur in any valid Scrabble word, and referencing it to immediately terminate iterating on sequences which contain an invalid sequence. 
  - Deduping letters in AI's hand before generating possible placements
  - Sorting the AI's hand by highest scoring letter first (which may or may not do anything 🤔.)
- At the end of the day, my AI's speed was acceptable, usually calculating all possible moves in 0-10 seconds.
- However, in the worst cases (such as, a very complex board state + an AI hand with many easy letters like "A", "E", and "BLANK"), the AI could take over 10 seconds to calculate all the possible moves.
- So, I ended up implementing an arbitrary 2 second timer for the AI's turn. Using this logic, the AI runs through as many possible moves as it can in 2 seconds, and spits out the highest scoring word it could find in that time. This 2 second timer was acceptable and fun to play against from a player's point of view. (if you pull down this repo and run it yourself, you can change the timer to whatever you want at the top of the `generateAIMove.ts` file.)
- Even with limiting the AI's calculation time to 2 seconds, it still consistently generated insane moves that I could barely comprehend, such as scoring 7 letter bingos, moves which create 3+ crosswords in addition to the main word, words that I didn't even know existed, etc. I got whooped every time I played against it, but it was still fun to see what words it would come up with.
- Fun fact: Scrabble AI is still an unsolved problem, and nobody has created a perfect AI so far. In fact, there are even entire research papers written on the topic. The reason it's so complex, is that there are so many different heuristics that need to be taken into account, such as what letters to save, what letters to redraw, how to setup the board to deny the opponent high scoring plays, etc. And accounting for all of these heuristics in a single AI is very difficult to do, and completely outside of my ability as a developer 😅. That being said, I'm pretty happy with my little self-made Scrabble AI.

## Available Scripts

### `npm start`

Runs the app in the development mode.\
Go to [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

# Getting Started with Create React App

This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).
