import { marked } from 'marked';
import DOMPurify from 'dompurify';

interface MarkdownRendererProps {
  content: string | Record<string, unknown> | null;
}

export default function MarkdownRenderer({ content }: MarkdownRendererProps) {
  if (!content) return null;

  // If it's an object, render as JSON
  if (typeof content === 'object' && content !== null) {
    return (
      <div className="p-4 bg-muted/50 border rounded-md">
        <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
          {JSON.stringify(content, null, 2)}
        </pre>
      </div>
    );
  }

  // If it's a string, try to parse as JSON first, then render as markdown
  if (typeof content === 'string') {
    try {
      // Try to parse as JSON
      const parsed = JSON.parse(content);
      return (
        <div className="p-4 bg-muted/50 border rounded-md">
          <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
            {JSON.stringify(parsed, null, 2)}
          </pre>
        </div>
      );
    } catch {
      // If not JSON, render as markdown
      marked.use({ breaks: true });
      const html = DOMPurify.sanitize(marked.parse(content) as string);
      return (
        <div
          className="p-4 bg-muted/50 border rounded-md prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      );
    }
  }

  return null;
}
