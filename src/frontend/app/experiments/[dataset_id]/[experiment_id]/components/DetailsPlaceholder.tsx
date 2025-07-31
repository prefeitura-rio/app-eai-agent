'use client';

import React from 'react';
import { List } from 'lucide-react';

export default function DetailsPlaceholder() {
    return (
        <div className="flex h-full items-center justify-center text-center text-muted-foreground py-16">
            <div>
                <List className="h-16 w-16 mx-auto" />
                <p className="mt-4">Selecione um run na lista à esquerda para ver os detalhes.</p>
            </div>
        </div>
    );
}
