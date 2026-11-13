// Keep the post-build canonical overrides (plugins/canonical-overrides.js) after react-helmet hydrates the head.
const MAP = {
  '/docs/guides/blind-zone-and-minimum-range/': 'https://erdilrf.com/knowledge/minimum-measuring-distance-blind-zone/',
  '/docs/platforms/ardupilot/': 'https://erdilrf.com/knowledge/connect-uart-laser-rangefinder-pixhawk-ardupilot/',
  '/docs/guides/905nm-vs-1535nm/': 'https://erdilrf.com/905nm-vs-1535nm-laser-rangefinder-module/',
};
function fix() {
  if (typeof document === 'undefined') return;
  let p = window.location.pathname;
  if (!p.endsWith('/')) p += '/';
  const target = MAP[p];
  if (!target) return;
  const links = document.querySelectorAll('link[rel="canonical"]');
  links.forEach((l, i) => { if (i > 0) l.remove(); });
  if (links[0]) links[0].setAttribute('href', target);
  else { const l = document.createElement('link'); l.rel = 'canonical'; l.href = target; document.head.appendChild(l); }
}
export function onRouteDidUpdate() {
  fix();
  setTimeout(fix, 300);
  setTimeout(fix, 1500);
}
