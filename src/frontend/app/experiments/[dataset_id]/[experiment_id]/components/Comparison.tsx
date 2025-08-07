'use client';

import React, { useState, useEffect } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { CardContent } from "@/components/ui/card";

interface ComparisonProps {
  content: string;
}

export default function Comparison({ content }: ComparisonProps) {
    const [contentHtml, setContentHtml] = useState('');

    useEffect(() => {
        const text = content || "";
        if (text) {
            marked.use({ breaks: true });
            const html = DOMPurify.sanitize(marked.parse(text) as string);
            console.log('Original text:', text);
            console.log('Parsed HTML:', html);
            setContentHtml(html);
        } else {
            setContentHtml("<p class='text-muted-foreground italic'>Nenhuma resposta disponível.</p>");
        }
    }, [content]);

    return (
        <CardContent 
            className="prose prose-base dark:prose-invert max-w-none whitespace-pre-wrap prose-base-custom" 
            dangerouslySetInnerHTML={{ __html: contentHtml }} 
        />
    );
}
