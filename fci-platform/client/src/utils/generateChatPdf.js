import { createElement } from 'react';
import { createRoot } from 'react-dom/client';
import html2pdf from 'html2pdf.js';
import ChatPdfContent from '../components/shared/ChatPdfContent';

/**
 * Generate and download a PDF transcript of chat messages.
 *
 * @param {Object} params
 * @param {Array}  params.messages  - Full messages array
 * @param {Object|null} params.metadata - Case metadata or null for free chat
 * @param {string} params.filename  - Output filename
 * @returns {Promise<void>}
 */
export default async function generateChatPdf({ messages, metadata, filename }) {
  // Filter out streaming / empty messages
  const printableMessages = messages.filter(
    (m) => !m.isStreaming && m.content?.trim()
  );

  if (printableMessages.length === 0) {
    throw new Error('No messages to export');
  }

  // Create hidden container — must stay in the viewport for html2canvas to capture it.
  // We wrap in an outer div that clips to 0x0 so the user never sees a flash,
  // while the inner container remains fully "visible" to html2canvas.
  const wrapper = document.createElement('div');
  wrapper.style.cssText =
    'position:fixed;left:0;top:0;width:0;height:0;overflow:hidden;z-index:-9999;pointer-events:none;';
  const container = document.createElement('div');
  container.style.cssText = 'width:210mm;background:#fff;';
  wrapper.appendChild(container);
  document.body.appendChild(wrapper);

  // Render ChatPdfContent into container
  const root = createRoot(container);
  root.render(
    createElement(ChatPdfContent, {
      messages: printableMessages,
      metadata,
    })
  );

  // Wait for React to paint
  await new Promise((r) => setTimeout(r, 150));

  // Generate PDF
  const options = {
    margin: 15,
    filename,
    image: { type: 'jpeg', quality: 0.95 },
    html2canvas: {
      scale: 2,
      useCORS: true,
      letterRendering: true,
      scrollX: 0,
      scrollY: 0,
      width: container.scrollWidth,
      height: container.scrollHeight,
    },
    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' },
    pagebreak: { mode: ['avoid-all', 'css', 'legacy'] },
  };

  await html2pdf().set(options).from(container).save();

  // Cleanup
  root.unmount();
  wrapper.remove();
}

/**
 * Build a filename for the PDF export.
 */
export function buildPdfFilename(metadata, conversationId) {
  const date = new Date().toISOString().slice(0, 10);
  if (metadata?.caseId) {
    return `FCI-${metadata.caseId}-transcript-${date}.pdf`;
  }
  const shortId = conversationId ? conversationId.slice(0, 8) : 'new';
  return `FCI-chat-${shortId}-${date}.pdf`;
}
