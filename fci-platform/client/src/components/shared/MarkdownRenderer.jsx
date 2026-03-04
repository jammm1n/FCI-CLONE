import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export default function MarkdownRenderer({ content, className = '' }) {
  if (!content) return null;

  return (
    <div className={`prose-invert text-base leading-relaxed ${className}`}>
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
          code: ({ node, children, className, ...props }) => {
            const isBlock = className?.startsWith('language-');
            if (!isBlock) {
              return (
                <code className="bg-surface-100 dark:bg-surface-750 px-1.5 py-0.5 rounded text-sm font-mono" {...props}>
                  {children}
                </code>
              );
            }
            return <code className={className} {...props}>{children}</code>;
          },
          pre: ({ children }) => (
            <pre className="bg-surface-50 dark:bg-surface-950 rounded-lg p-4 overflow-x-auto text-sm my-3">
              {children}
            </pre>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
