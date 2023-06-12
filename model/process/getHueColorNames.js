const fs = require('fs'),
  refine = require('./refine.js'),
  colorBins = require('./colorBins.js'),
  csv = require("csvtojson");
  // Converter = require("csvtojson").Converter;
// const converter = new Converter({});
const N_BINS = 36, N_TERMS = 20;
const O_FILE_NAME = `../hue_color_names_aggregated.json`;
const O_FILE_NAME_FLATTEN = `../hue_color_names.json`;

import('d3').then(d3 => {

const LANG_CODE = {
  'English (English)' : "en",
  'Korean (한국어, 조선어)' : "ko",
  'Spanish (español)': "es",
  'German (Deutsch)': "de",
  'French (français, langue française)': "fr",
  'Chinese (中文 (Zhōngwén), 汉语, 漢語)': "zh-CN",
  'Swedish (svenska)' : "sv",
  'Portuguese (português)' : "pt",
  'Polish (język polski, polszczyzna)': "pl",
  'Russian (Русский)' : "ru",
  'Dutch (Nederlands, Vlaams)': "nl",
  'Finnish (suomi, suomen kieli)': "fi",
  'Arabic (العربية)' : "ar",
  'Romanian (limba română)' : "ro",
  'Danish (dansk)': "da",
  'Italian (italiano)': "it",
  'Persian (Farsi) (فارسی)': 'fa',
  'English (text-davinci-003)': 'en-gpt',
  'Chinese (text-davinci-003)': 'zh-CN-gpt',
  'Russian (text-davinci-003)': 'ru-gpt',
  'Korean (text-davinci-003)': 'ko-gpt',
};

// const TOP_LANGS = ['English (English)' ,
//  'Korean (한국어, 조선어)' ,
//  'Spanish (español)',
//  'German (Deutsch)',
//  'French (français, langue française)',
//  'Chinese (中文 (Zhōngwén), 汉语, 漢語)',
//  'Swedish (svenska)' ,
//  'Portuguese (português)' ,
//  'Polish (język polski, polszczyzna)',
//  'Russian (Русский)' ,
//  'Dutch (Nederlands, Vlaams)',
//  'Finnish (suomi, suomen kieli)',
//  'Romanian (limba română)' ,
//  'Persian (Farsi) (فارسی)'];
const TOP_LANGS = ['English (text-davinci-003)',
'Chinese (text-davinci-003)',
'Russian (text-davinci-003)',
'Korean (text-davinci-003)',];

// fs.createReadStream("../../raw/color_perception_table_color_names.csv").pipe(converter);
csv()
    .fromStream(fs.createReadStream("../../gpt-data/text-davinci-003_results.csv"))
    .then(colorNames => {
// converter.on("end_parsed", function (colorNames) {
    // 1. Get top languages
    let grouped = Array.from(d3.group(colorNames, d => d.lang0))
      .sort((a,b) =>  - a[1].length + b[1].length)
      .filter(g => TOP_LANGS.indexOf(g[0]) >=0 );

    // 2. Get top terms
    grouped.forEach(g => {
      let refined = refine(g[1], "line");
      let nested = Array.from(d3.group(refined, v => v.name))
        .map(([key, values]) => ({ key, values }))
        .sort((a,b) => -a.values.length + b.values.length);

      g[1] = {terms: nested};
      let rankLookUp = g[1].terms.map(t => t.values.length);
      g[1].topNTerms = g[1].terms.filter(t => rankLookUp.indexOf(t.values.length) + 1 <= N_TERMS);

      g[1].terms.forEach(t => {
        t.rank = rankLookUp.indexOf(t.values.length) + 1;
      });

      //Print out the terms
      console.log(`Lang : ${g[0]}`);
      console.log(`Terms : ${JSON.stringify(g[1].topNTerms.map(subg => subg.key))}`);
    });


  // 3. Export the data
  let bin = colorBins.genBin(N_BINS);
  let result = {};
  let flatten = [];

  grouped.forEach(group => {
    let bufFlatten = [];
    let terms = [];
    let mapped = {
      'colorNameCount': [],
      'terms': [],
      'totalCount' : 0,
      'avgColor': []
    }
    group.topNTerms.forEach(term => {
      mapped.terms.push(term.key);
      let colorNameCnt = new Array(N_BINS).fill(0);
      let [l, a, b] = [0, 0, 0];
      term.values.forEach(response => {
        colorNameCnt[colorBins.binNum(response, bin)] += 1;
        let lab = d3.lab(d3.color(`rgb(${[response.r, response.g, response.b].map(Math.floor).join(",")})`));
        l += lab.l;
        a += lab.a;
        b += lab.b;
      });
      let avgLABColor = d3.lab(l/term.values.length, a/term.values.length, b/term.values.length);
      let avgRGBColor = d3.color(avgLABColor);
      mapped.avgColor.push({
        "r": avgRGBColor.r, "g": avgRGBColor.g, "b": avgRGBColor.b
      });
      mapped.colorNameCount.push(colorNameCnt);
      mapped.totalCount += term.values.length;
      for (var i = 0; i < N_BINS; i++) {
        bufFlatten.push({
          "lang": group.key,
          "term": term.key,
          "rank": term.rank,
          "binNum": i,
          "cnt": colorNameCnt[i],
          "pCT": colorNameCnt[i] / term.values.length
        });
      }
      terms.push({
        "term": term.key,
        "modeBinNum": colorNameCnt.indexOf(d3.max(colorNameCnt))
      });
    });
    terms.sort((a,b) => a.modeBinNum - b.modeBinNum);
    bufFlatten.forEach( d => {
      d.termSubID = terms.findIndex(t => t.term === d.term);
      d.pTC = d.cnt / d3.sum(bufFlatten.filter(d2 => d2.binNum === d.binNum), x => x.cnt);
    });
    flatten = flatten.concat(bufFlatten);
    result[group.key] = mapped;
  });


  result.colorSet = bin.map(function(index, i, array){
    return colorBins.colorSet[Math.round(i===0 ? index/2 : (index + array[i-1]) / 2)];
  });

  fs.writeFileSync(O_FILE_NAME, JSON.stringify(result, null, 2));
  fs.writeFileSync(O_FILE_NAME_FLATTEN, JSON.stringify(flatten, null, 2));

});

});