const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';

// generates all permutations of a sequence including 0, 1, or 2 blanks,
// then runs cb() on each permutation.
export const forEverySequencePermutation = (text:string, cb:Function) => {
  const firstBlankIndex = text.indexOf('_');
  const secondBlankIndex = text.lastIndexOf('_');
  
  if (firstBlankIndex !== -1) {
    for (let i = 0; i < 26; i++) {
      const text1 = `${text.slice(0, firstBlankIndex)}${alphabet[i]}${text.slice(firstBlankIndex + 1)}`;
      if (secondBlankIndex !== -1 && firstBlankIndex !== secondBlankIndex) {
        for (let j = 0; j < 26; j++) {
          cb(`${text1.slice(0, secondBlankIndex)}${alphabet[j]}${text.slice(secondBlankIndex + 1)}`);
        }
      } else {
        cb(text1);
      }
    }
  } else {
    cb(text);
  }
};
