import { marked } from 'marked';

interface MarkdownRendererProps {
  content: string | Record<string, unknown>;
}

export default async function MarkdownRenderer({ content }: MarkdownRendererProps) {
  // Convert object to formatted string if needed
  let contentString: string;
  if (typeof content === 'string') {
    contentString = content;
  } else {
    contentString = JSON.stringify(content, null, 2);
  }
  
  const html = await marked(contentString);
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
