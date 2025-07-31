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
            setContentHtml(DOMPurify.sanitize(marked.parse(text) as string));
        } else {
            setContentHtml("<p class='text-muted-foreground italic'>Nenhuma resposta disponível.</p>");
        }
    }, [content]);

    return (
        <CardContent className="prose text-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: contentHtml }} />
    );
}
