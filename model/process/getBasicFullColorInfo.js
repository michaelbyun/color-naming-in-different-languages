// Need to install 'csvtojson' and 'csv-write-stream'
// npm install csvtojson
// npm install csv-write-stream

const fs = require('fs'),
  refine = require('./refine.js'),
  csv = require("csvtojson"),
  // d3 = require('d3'),
  csvWriter = require('csv-write-stream');

import('d3').then(d3 => {

  const MIN_FULL_COLOR_NAMES = 12;
  const LINE_RGB_SET = "line";
  const FULL_RGB_SET = "full";

  // Path or the input csv file
  const FILE_I = "../cleaned_color_names.csv"
  const FILE_O = "../basic_full_color_info.csv"; // Path for the output

  csv().fromFile(FILE_I)
    .then((colorNames)=>{

      let grouped = Array.from(d3.group(colorNames, d => d.lang0))
                         .sort((a, b) =>  - a[1].length + b[1].length);

      grouped.forEach(g => {
        let terms = Array.from(d3.group(g[1], v => v.name))
                         .sort((a, b) => -a[1].length + b[1].length);

        g[1] = terms.map(term => {
          let numLineNames = term[1].filter(entry => entry.rgbSet == LINE_RGB_SET).length;
          let numFullNames = term[1].filter(entry => entry.rgbSet == FULL_RGB_SET).length;
          let simplifiedName = term[0];

          let commonName = Array.from(d3.group(term[1], t => t.entered_name))
                               .sort((a,b) => -a[1].length + b[1].length)[0][0];

          return {
            terms: term[1],
            numLineNames: numLineNames,
            numFullNames: numFullNames,
            simplifiedName: simplifiedName,
            commonName: commonName
          };
        });

        g[1] = g[1].filter(g_term => g_term.numFullNames >= MIN_FULL_COLOR_NAMES);
        g[1].sort((a,b) => -a.numFullNames + b.numFullNames);
      });

      grouped.sort((a,b) =>  - a[1].length + b[1].length);

      console.log("writing file");
      let writer = csvWriter();
      writer.pipe(fs.createWriteStream(FILE_O));

      grouped.forEach(lang => {
        lang[1].forEach(term => {
          delete term.terms;
          term.lang = lang[0];
          writer.write({
            lang: term.lang,
            commonName: term.commonName,
            simplifiedName: term.simplifiedName,
            numFullNames: term.numFullNames,
            numLineNames: term.numLineNames,
          });
        })
      });

      writer.end();
    });
});