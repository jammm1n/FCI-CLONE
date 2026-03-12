import { useState, useCallback, useRef, createElement } from 'react';
import { createRoot } from 'react-dom/client';
import html2canvas from 'html2canvas';
import MarkdownRenderer from '../shared/MarkdownRenderer';

const DOWNLOAD_TABS = new Set(['elliptic_raw']);

// Column width in pixels for the rendered image.
// Content is split into columns of this width to produce a readable, compact PNG.
const COL_WIDTH = 380;
const COL_GAP = 24;
const IMG_PADDING = 32;

// Split markdown into N roughly equal groups, breaking at ## or ### headings.
// Falls back to blank-line splits if no headings found.
function splitMarkdownIntoColumns(markdown, numCols) {
  const lines = markdown.split('\n');

  // Find safe split points: ## or ### headings, or blank lines before content
  const breakpoints = [0];
  for (let i = 1; i < lines.length; i++) {
    if (/^#{2,3}\s/.test(lines[i])) {
      breakpoints.push(i);
    }
  }

  // If not enough heading breakpoints, also use blank lines
  if (breakpoints.length < numCols + 1) {
    for (let i = 1; i < lines.length; i++) {
      if (lines[i].trim() === '' && i + 1 < lines.length && lines[i + 1].trim() !== '') {
        if (!breakpoints.includes(i + 1)) {
          breakpoints.push(i + 1);
        }
      }
    }
    breakpoints.sort((a, b) => a - b);
  }

  // Target: roughly equal line counts per column
  const linesPerCol = Math.ceil(lines.length / numCols);
  const columns = [];

  for (let col = 0; col < numCols; col++) {
    const idealStart = col * linesPerCol;
    const idealEnd = (col + 1) * linesPerCol;

    // Find nearest breakpoint to idealStart
    let start;
    if (col === 0) {
      start = 0;
    } else {
      start = breakpoints.reduce((best, bp) =>
        Math.abs(bp - idealStart) < Math.abs(best - idealStart) ? bp : best
      , breakpoints[0]);
    }

    // Find nearest breakpoint to idealEnd
    let end;
    if (col === numCols - 1) {
      end = lines.length;
    } else {
      end = breakpoints.reduce((best, bp) =>
        Math.abs(bp - idealEnd) < Math.abs(best - idealEnd) ? bp : best
      , breakpoints[0]);
      // Don't let end go backwards past start
      if (end <= start) end = Math.min(idealEnd, lines.length);
    }

    columns.push(lines.slice(start, end).join('\n'));
  }

  // Remove any empty columns and merge any leftover lines
  return columns.filter(c => c.trim());
}

async function downloadAsImage(content, hiddenRef) {
  const container = hiddenRef.current;
  if (!container) return;

  container.innerHTML = '';
  container.style.width = `${COL_WIDTH}px`;
  container.style.display = 'block';

  // Step 1: render single-column to measure total content height
  const measureDiv = document.createElement('div');
  container.appendChild(measureDiv);
  const root = createRoot(measureDiv);
  await new Promise(resolve => {
    root.render(createElement(MarkdownRenderer, { content, className: 'max-w-none' }));
    requestAnimationFrame(() => requestAnimationFrame(resolve));
  });

  const singleColHeight = measureDiv.scrollHeight;
  root.unmount();

  // Target column height ≈ 1200px — produces a readable, landscape-ish image
  const targetHeight = 1200;
  const numCols = Math.max(2, Math.ceil(singleColHeight / targetHeight));

  // Step 2: split markdown into columns
  const columns = splitMarkdownIntoColumns(content, numCols);
  const actualCols = columns.length;

  // Step 3: build a grid in the hidden div with one MarkdownRenderer per column
  container.innerHTML = '';
  const totalWidth = actualCols * COL_WIDTH + (actualCols - 1) * COL_GAP + IMG_PADDING * 2;
  container.style.width = `${totalWidth}px`;
  container.style.padding = `${IMG_PADDING}px`;
  container.style.display = 'grid';
  container.style.gridTemplateColumns = `repeat(${actualCols}, ${COL_WIDTH}px)`;
  container.style.gap = `${COL_GAP}px`;
  container.style.background = '#1a1a1f'; // surface-900 equivalent
  container.style.color = '#e5e5ea'; // light text
  container.style.fontFamily = "'Plus Jakarta Sans', sans-serif";
  container.style.fontSize = '13px';
  container.style.lineHeight = '1.6';

  // Render each column
  const colRoots = [];
  for (const colContent of columns) {
    const colDiv = document.createElement('div');
    colDiv.style.overflowWrap = 'break-word';
    colDiv.style.minWidth = '0';
    container.appendChild(colDiv);

    const colRoot = createRoot(colDiv);
    colRoot.render(createElement(MarkdownRenderer, { content: colContent, className: 'max-w-none' }));
    colRoots.push(colRoot);
  }

  // Wait for render
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));

  // Step 4: capture to canvas
  const canvas = await html2canvas(container, {
    backgroundColor: '#1a1a1f',
    scale: 2, // retina quality
    useCORS: true,
    logging: false,
  });

  // Cleanup
  colRoots.forEach(r => r.unmount());
  container.innerHTML = '';
  container.style.display = 'none';

  // Step 5: download
  const link = document.createElement('a');
  link.download = `elliptic-screening-${new Date().toISOString().slice(0, 10)}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

export default function CaseDataPanel({ content, activeTab }) {
  const [downloading, setDownloading] = useState(false);
  const hiddenRef = useRef(null);

  const showDownload = DOWNLOAD_TABS.has(activeTab) && !!content;

  const handleDownload = useCallback(async () => {
    if (downloading || !content) return;
    setDownloading(true);
    try {
      await downloadAsImage(content, hiddenRef);
    } catch (err) {
      console.error('Screenshot download failed:', err);
    } finally {
      setDownloading(false);
    }
  }, [content, downloading]);

  if (!content) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-10 h-10 mx-auto mb-2 text-surface-300 dark:text-surface-600 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <p className="text-sm text-surface-400">Select a data tab to view case information.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 bg-surface-100 dark:bg-surface-850 relative grain-texture" style={{ scrollBehavior: 'smooth' }}>
        {showDownload && (
          <button
            onClick={handleDownload}
            disabled={downloading}
            title="Download as image"
            className="absolute top-3 right-3 z-20 p-1.5 rounded-md bg-surface-200/80 dark:bg-surface-700/80 hover:bg-surface-300 dark:hover:bg-surface-600 text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-200 transition-colors disabled:opacity-50"
          >
            {downloading ? (
              <svg className="w-4 h-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
              </svg>
            )}
          </button>
        )}
        <div key={activeTab} className="relative z-10 animate-fade-in">
          <MarkdownRenderer content={content} />
        </div>
      </div>

      {/* Hidden off-screen container for image rendering */}
      <div
        ref={hiddenRef}
        style={{
          position: 'fixed',
          left: '-99999px',
          top: 0,
          display: 'none',
          zIndex: -1,
        }}
      />
    </>
  );
}
