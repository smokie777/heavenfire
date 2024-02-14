// run this file using: node generateTwl06InvalidSequencesJSON.js > twl06InvalidSequences.ts

// this script creates a dictionary of all 2, 3, and 4 letter sequences which do not exist in any valid scrabble word.
// the purpose of having this information is to speed up the scrabble ai by removing unnecessary iterations.

const fs = require('fs');

fs.readFile('twl06.txt', 'utf8', function(err, data) {
  if (err) throw err;
  const lines = data.toUpperCase().split(/\r?\n/);

  const sequences = {};
  const invalidSequences = {};
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

  letters.forEach(a => {
    letters.forEach(b => {
      sequences[`${a}${b}`] = false;
      letters.forEach(c => {
        sequences[`${a}${b}${c}`] = false;
        letters.forEach(d => {
          sequences[`${a}${b}${c}${d}`] = false;
        });
      });
    });
  });

  lines.forEach(word => {
    if (word.length <= 4) {
      sequences[word] = true;
    }

    [2, 3, 4].forEach(sequenceLength => {
      for (let i = 0; i <= word.length - sequenceLength; i++) {
        sequences[word.slice(i, i + sequenceLength)] = true;
      }
    });
  });

  Object.keys(sequences).forEach(i => {
    if (!sequences[i]) {
      invalidSequences[i] = true;
    }
  });

  console.log(invalidSequences);
  // console.log(`${Object.keys(invalidSequences).length}/${Object.keys(sequences).length} sequences are invalid`);
});
