// run this file using: node generateTwl06JSON.js

const fs = require('fs');

fs.readFile('twl06.txt', 'utf8', function(err, data) {
  if (err) throw err;
  const lines = data.split(/\r?\n/).map(i => `'${i.toUpperCase()}':true,`);

  fs.writeFile('twl06.ts', lines.join('\n'), err => {
    if (err) {
      console.error(err);
    }
    // file written successfully
  });
});
