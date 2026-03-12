import TurndownService from 'turndown';
import { gfm } from 'turndown-plugin-gfm';

const turndown = new TurndownService({
  headingStyle: 'atx',
  codeBlockStyle: 'fenced',
});
turndown.use(gfm);

/**
 * If the clipboard contains HTML with meaningful formatting (tables, lists, etc.),
 * convert it to Markdown. Returns the markdown string, or null to let default
 * text/plain paste happen.
 */
export function getMarkdownFromPaste(clipboardData) {
  const html = clipboardData?.getData('text/html');
  if (!html) return null;

  // Only convert when HTML has formatting worth preserving
  if (/<(table|th|td|tr|ol|ul|li|h[1-6]|strong|em|b|i|a\s)/i.test(html)) {
    return turndown.turndown(html);
  }

  return null;
}
