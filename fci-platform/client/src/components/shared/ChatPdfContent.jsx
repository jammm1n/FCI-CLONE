import MarkdownRenderer from './MarkdownRenderer';
import { formatTimestamp } from '../../utils/formatters';

const GOLD = '#F0B90B';

const styles = {
  page: {
    fontFamily: "'Plus Jakarta Sans', 'Segoe UI', Arial, sans-serif",
    backgroundColor: '#ffffff',
    color: '#1a1a1a',
    fontSize: '13px',
    lineHeight: '1.6',
    padding: '0',
  },
  header: {
    marginBottom: '24px',
    paddingBottom: '16px',
  },
  title: {
    fontSize: '22px',
    fontWeight: '700',
    margin: '0 0 2px 0',
    color: '#1a1a1a',
  },
  subtitle: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#666666',
    margin: '0 0 12px 0',
  },
  accentLine: {
    height: '3px',
    backgroundColor: GOLD,
    border: 'none',
    margin: '12px 0 16px 0',
    borderRadius: '2px',
  },
  metaTable: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '12px',
    marginBottom: '8px',
  },
  metaLabel: {
    padding: '4px 12px 4px 0',
    fontWeight: '600',
    color: '#666666',
    whiteSpace: 'nowrap',
    verticalAlign: 'top',
    width: '140px',
  },
  metaValue: {
    padding: '4px 0',
    color: '#1a1a1a',
  },
  messageBlock: {
    marginBottom: '16px',
    padding: '12px 16px',
    borderRadius: '8px',
    pageBreakInside: 'avoid',
  },
  userMessage: {
    backgroundColor: '#fef9e7',
    border: '1px solid #fdf0c4',
  },
  assistantMessage: {
    backgroundColor: '#f8f9fa',
    border: '1px solid #e9ecef',
  },
  roleLine: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '6px',
    fontSize: '11px',
    fontWeight: '600',
  },
  userRole: { color: '#b8860b' },
  assistantRole: { color: '#6b7280' },
  timestamp: {
    fontWeight: '400',
    color: '#999999',
    fontSize: '10px',
  },
  messageContent: {
    fontSize: '13px',
    lineHeight: '1.6',
    color: '#1a1a1a',
    wordBreak: 'break-word',
  },
  toolsUsed: {
    marginTop: '8px',
    fontStyle: 'italic',
    fontSize: '11px',
    color: '#888888',
  },
  footer: {
    marginTop: '32px',
    paddingTop: '12px',
    borderTop: `2px solid ${GOLD}`,
    textAlign: 'center',
    fontSize: '10px',
    color: '#999999',
  },
};

export default function ChatPdfContent({ messages, metadata }) {
  const isCase = metadata !== null && metadata !== undefined;
  const now = new Date().toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>FCI Investigation Platform</h1>
        <p style={styles.subtitle}>
          {isCase ? 'Case Transcript' : 'Chat Transcript'}
        </p>
        <hr style={styles.accentLine} />

        <table style={styles.metaTable}>
          <tbody>
            {isCase && metadata.caseId && (
              <tr>
                <td style={styles.metaLabel}>Case ID</td>
                <td style={styles.metaValue}>{metadata.caseId}</td>
              </tr>
            )}
            {isCase && metadata.caseType && (
              <tr>
                <td style={styles.metaLabel}>Case Type</td>
                <td style={styles.metaValue}>{metadata.caseType.toUpperCase()}</td>
              </tr>
            )}
            {isCase && metadata.subjectUserId && (
              <tr>
                <td style={styles.metaLabel}>Subject</td>
                <td style={styles.metaValue}>{metadata.subjectUserId}</td>
              </tr>
            )}
            {isCase && metadata.status && (
              <tr>
                <td style={styles.metaLabel}>Status</td>
                <td style={styles.metaValue}>{metadata.status.replace('_', ' ').toUpperCase()}</td>
              </tr>
            )}
            {metadata?.investigator && (
              <tr>
                <td style={styles.metaLabel}>Investigator</td>
                <td style={styles.metaValue}>{metadata.investigator}</td>
              </tr>
            )}
            <tr>
              <td style={styles.metaLabel}>Generated</td>
              <td style={styles.metaValue}>{now}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Messages */}
      {messages.map((msg, idx) => {
        const isUser = msg.role === 'user';
        const isLong = (msg.content || '').length > 2000;
        const blockStyle = {
          ...styles.messageBlock,
          ...(isUser ? styles.userMessage : styles.assistantMessage),
          ...(isLong ? { pageBreakInside: 'auto' } : {}),
        };

        return (
          <div key={msg.message_id || idx} style={blockStyle}>
            <div style={styles.roleLine}>
              <span style={isUser ? styles.userRole : styles.assistantRole}>
                {isUser ? 'Investigator' : 'AI Assistant'}
              </span>
              <span style={styles.timestamp}>
                {formatTimestamp(msg.timestamp)}
              </span>
            </div>

            <div style={styles.messageContent}>
              {isUser ? (
                <>
                  {msg.images?.length > 0 && (
                    <p style={{ fontStyle: 'italic', color: '#888' }}>[Image attachment]</p>
                  )}
                  <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</p>
                </>
              ) : (
                <MarkdownRenderer content={msg.content} />
              )}
            </div>

            {!isUser && msg.tools_used?.length > 0 && (
              <div style={styles.toolsUsed}>
                Tools used: {msg.tools_used.map((t) => t.document_title || t.tool).join(', ')}
              </div>
            )}
          </div>
        );
      })}

      {/* Footer */}
      <div style={styles.footer}>
        <p style={{ margin: '0 0 2px 0', fontWeight: '600' }}>
          CONFIDENTIAL — For authorized use only
        </p>
        <p style={{ margin: 0 }}>
          Generated {now}
        </p>
      </div>
    </div>
  );
}
