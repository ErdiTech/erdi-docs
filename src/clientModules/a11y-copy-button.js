// Give icon-only copy buttons an accessible name (axe: button-name). Runs after every route change.
function label() {
  if (typeof document === 'undefined') return;
  document.querySelectorAll('.copyPageButton, button[class*="copyButton"]').forEach((b) => {
    if (!b.getAttribute('aria-label') && !(b.textContent || '').trim()) {
      b.setAttribute('aria-label', b.className.indexOf('copyPage') >= 0 ? 'Copy page as Markdown' : 'Copy code to clipboard');
    }
  });
}
export function onRouteDidUpdate() {
  label();
  setTimeout(label, 500);
}
