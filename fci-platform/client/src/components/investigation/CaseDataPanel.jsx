import MarkdownRenderer from '../shared/MarkdownRenderer';

export default function CaseDataPanel({ content }) {
  if (!content) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-sm text-surface-500">Select a data tab to view case information.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
      <MarkdownRenderer content={content} />
    </div>
  );
}
