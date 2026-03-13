import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

function extractText(children) {
  if (typeof children === 'string') return children;
  if (Array.isArray(children)) return children.map(extractText).join('');
  if (children?.props?.children) return extractText(children.props.children);
  return '';
}

function IcrBlock({ children }) {
  const [copied, setCopied] = useState(false);
  const rawText = extractText(children).replace(/\n$/, '');

  const handleCopy = async () => {
    await navigator.clipboard.writeText(rawText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-3 rounded-lg border border-gold-500/30 dark:border-gold-400/25 bg-surface-50 dark:bg-surface-850 px-5 py-4">
      <button
        onClick={handleCopy}
        className="absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium transition-colors
          bg-surface-200 dark:bg-surface-700 text-surface-600 dark:text-surface-300
          hover:bg-gold-100 hover:text-gold-700 dark:hover:bg-gold-500/20 dark:hover:text-gold-400"
      >
        {copied ? 'Copied!' : 'Copy'}
      </button>
      <div className="whitespace-pre-wrap text-base leading-relaxed text-surface-800 dark:text-surface-200 pr-16">
        {children}
      </div>
    </div>
  );
}

export default function MarkdownRenderer({ content, className = '' }) {
  if (!content) return null;

  return (
    <div className={`dark:prose-invert text-base leading-relaxed ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          table: ({ children }) => (
            <div className="rounded-lg overflow-hidden border border-surface-200 dark:border-surface-700 my-3">
              <table className="w-full">{children}</table>
            </div>
          ),
          th: ({ children }) => (
            <th className="bg-surface-100 dark:bg-surface-800 font-semibold py-2.5 px-4 text-sm text-left">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="py-2.5 px-4 text-sm border-t border-surface-200 dark:border-surface-700">
              {children}
            </td>
          ),
          h2: ({ children }) => (
            <h2 className="text-lg font-semibold mt-5 mb-2">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-base font-semibold mt-4 mb-2">{children}</h3>
          ),
          code: ({ node, children, className: codeClassName, ...props }) => {
            if (codeClassName === 'language-icr') {
              return <span {...props}>{children}</span>;
            }
            const isBlock = codeClassName?.startsWith('language-');
            if (!isBlock) {
              return (
                <code className="bg-surface-100 dark:bg-surface-750 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                  {children}
                </code>
              );
            }
            return <code className={codeClassName} {...props}>{children}</code>;
          },
          pre: ({ children }) => {
            const childProps = children?.props;
            if (childProps?.className === 'language-icr') {
              return <IcrBlock>{childProps.children}</IcrBlock>;
            }
            return (
              <pre className="bg-surface-50 dark:bg-surface-900 rounded-lg p-4 overflow-x-auto text-sm my-3">
                {children}
              </pre>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
