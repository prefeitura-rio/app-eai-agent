'use client';

import React from 'react';
import { User, Bot } from 'lucide-react';

interface Turn {
    turn: number;
    judge_message: string;
    agent_response: string;
}

interface ConversationTranscriptProps {
    transcript: Turn[] | null;
}

export default function ConversationTranscript({ transcript }: ConversationTranscriptProps) {
    if (!transcript || transcript.length === 0) {
        return <p className="text-sm text-muted-foreground p-4">Nenhuma transcrição de conversa disponível.</p>;
    }

    return (
        <div className="space-y-4">
            {transcript.map((turn) => (
                <div key={turn.turn}>
                    {/* Judge's Message (User) */}
                    <div className="flex items-start gap-3 justify-end mb-2">
                        <div className="max-w-[80%] rounded-lg bg-primary text-primary-foreground p-3">
                            <p className="text-sm">{turn.judge_message}</p>
                        </div>
                        <User className="h-6 w-6 flex-shrink-0" />
                    </div>

                    {/* Agent's Response */}
                    <div className="flex items-start gap-3">
                        <Bot className="h-6 w-6 text-primary flex-shrink-0" />
                        <div className="max-w-[80%] rounded-lg bg-muted p-3">
                             <p className="text-sm">{turn.agent_response}</p>
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
