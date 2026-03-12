import { useState, useCallback, useRef, createElement } from 'react';
import { createRoot } from 'react-dom/client';
import html2canvas from 'html2canvas';
import MarkdownRenderer from '../shared/MarkdownRenderer';

const DOWNLOAD_TABS = new Set(['elliptic_raw']);

const STRIP_WIDTH = 400;  // px width per column strip in the output image
const STRIP_GAP = 16;     // px gap between strips
const PAD = 24;            // px padding around the whole image
const BG_COLOR = '#1a1a1f';
const TARGET_COLS = 10;    // number of columns in the output image

// Find a "safe" cut row near targetY — a row where all pixels match background.
// Scans up to `range` pixels above and below targetY.
function findSafeCut(ctx, targetY, width, height, range = 80) {
  const bgSample = ctx.getImageData(0, 0, 1, 1).data; // top-left = background
  const tolerance = 30;

  const match = (r, g, b) =>
    Math.abs(r - bgSample[0]) < tolerance &&
    Math.abs(g - bgSample[1]) < tolerance &&
    Math.abs(b - bgSample[2]) < tolerance;

  // Search outward from targetY: check targetY, targetY-1, targetY+1, targetY-2, ...
  for (let offset = 0; offset <= range; offset++) {
    for (const dir of [0, -1, 1]) {
      const y = targetY + offset * (dir || 1);
      if (y < 0 || y >= height) continue;

      const row = ctx.getImageData(0, y, width, 1).data;
      let safe = true;
      // Sample every 4th pixel for speed
      for (let x = 0; x < width * 4; x += 16) {
        if (!match(row[x], row[x + 1], row[x + 2])) { safe = false; break; }
      }
      if (safe) return y;
    }
  }
  return targetY; // fallback: cut at exact target
}

async function downloadAsImage(content, hiddenRef, caseName) {
  const container = hiddenRef.current;
  if (!container) return;

  // Step 1: render full content as one tall column
  container.innerHTML = '';
  Object.assign(container.style, {
    display: 'block',
    width: `${STRIP_WIDTH}px`,
    padding: '16px',
    background: BG_COLOR,
    color: '#e5e5ea',
    fontFamily: "'Plus Jakarta Sans', sans-serif",
    fontSize: '13px',
    lineHeight: '1.6',
    overflowWrap: 'break-word',
  });

  const renderDiv = document.createElement('div');
  container.appendChild(renderDiv);

  const root = createRoot(renderDiv);
  root.render(createElement(MarkdownRenderer, { content, className: 'max-w-none' }));
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));

  // Step 2: capture the tall single column to a canvas
  const tallCanvas = await html2canvas(container, {
    backgroundColor: BG_COLOR,
    scale: 2,
    useCORS: true,
    logging: false,
  });

  root.unmount();
  container.innerHTML = '';
  container.style.display = 'none';

  const srcW = tallCanvas.width;
  const srcH = tallCanvas.height;
  const srcCtx = tallCanvas.getContext('2d');

  // Step 3: find safe cut points — divide into TARGET_COLS strips
  const numStrips = TARGET_COLS;
  const idealStripH = Math.ceil(srcH / numStrips);

  const cuts = [0];
  for (let i = 1; i < numStrips; i++) {
    const idealY = i * idealStripH;
    cuts.push(findSafeCut(srcCtx, idealY, srcW, srcH));
  }
  cuts.push(srcH);

  // Step 4: calculate strip heights and find the tallest
  const stripHeights = [];
  for (let i = 0; i < cuts.length - 1; i++) {
    stripHeights.push(cuts[i + 1] - cuts[i]);
  }
  const maxStripH = Math.max(...stripHeights);

  // Step 5: stitch strips side by side into output canvas
  const scaledPad = PAD * 2;
  const scaledGap = STRIP_GAP * 2;
  const outW = numStrips * srcW + (numStrips - 1) * scaledGap + scaledPad * 2;
  const outH = maxStripH + scaledPad * 2;

  const outCanvas = document.createElement('canvas');
  outCanvas.width = outW;
  outCanvas.height = outH;
  const outCtx = outCanvas.getContext('2d');

  // Fill background
  outCtx.fillStyle = BG_COLOR;
  outCtx.fillRect(0, 0, outW, outH);

  // Draw each strip
  for (let i = 0; i < numStrips; i++) {
    const sx = 0;
    const sy = cuts[i];
    const sh = stripHeights[i];
    const dx = scaledPad + i * (srcW + scaledGap);
    const dy = scaledPad;
    outCtx.drawImage(tallCanvas, sx, sy, srcW, sh, dx, dy, srcW, sh);
  }

  // Step 6: download
  const link = document.createElement('a');
  const safeName = (caseName || 'unknown').replace(/[^a-zA-Z0-9_-]/g, '_');
  link.download = `Elliptic Screening - ${safeName}.png`;
  link.href = outCanvas.toDataURL('image/png');
  link.click();
}

export default function CaseDataPanel({ content, activeTab, caseName }) {
  const [downloading, setDownloading] = useState(false);
  const hiddenRef = useRef(null);

  const showDownload = DOWNLOAD_TABS.has(activeTab) && !!content;

  const handleDownload = useCallback(async () => {
    if (downloading || !content) return;
    setDownloading(true);
    try {
      await downloadAsImage(content, hiddenRef, caseName);
    } catch (err) {
      console.error('Screenshot download failed:', err);
    } finally {
      setDownloading(false);
    }
  }, [content, downloading, caseName]);

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
