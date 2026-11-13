// Point a few docs pages' rel=canonical at the main erdilrf.com page that owns the query
// (D3 cannibalization.csv, 2026-11-13). Runs after build so synced markdown can be regenerated freely.
const fs = require('fs');
const path = require('path');

const MAP = {
  'guides/blind-zone-and-minimum-range': 'https://erdilrf.com/knowledge/minimum-measuring-distance-blind-zone/',
  'platforms/ardupilot': 'https://erdilrf.com/knowledge/connect-uart-laser-rangefinder-pixhawk-ardupilot/',
  'guides/905nm-vs-1535nm': 'https://erdilrf.com/905nm-vs-1535nm-laser-rangefinder-module/',
};

module.exports = function canonicalOverrides() {
  return {
    name: 'canonical-overrides',
    async postBuild({outDir}) {
      for (const [route, target] of Object.entries(MAP)) {
        const file = path.join(outDir, route, 'index.html');
        if (!fs.existsSync(file)) throw new Error('canonical-overrides: missing ' + file);
        let html = fs.readFileSync(file, 'utf8');
        const re = /<link[^>]*rel=["']?canonical["']?[^>]*>/gi;
        const n = (html.match(re) || []).length;
        html = html.replace(re, '');
        html = html.replace('</head>', `<link rel="canonical" href="${target}"></head>`);
        fs.writeFileSync(file, html);
        console.log(`[canonical-overrides] ${route} -> ${target} (replaced ${n})`);
      }
    },
  };
};
