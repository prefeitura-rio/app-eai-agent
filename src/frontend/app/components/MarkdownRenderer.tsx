import { marked } from 'marked';

interface MarkdownRendererProps {
  content: string;
}

export default async function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const html = await marked(content);
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
