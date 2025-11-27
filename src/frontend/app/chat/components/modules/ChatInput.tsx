import React, { useEffect, useState } from 'react';
import { CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Send } from 'lucide-react';

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  requestStartTime: number | null;
  onSendMessage: (e: React.FormEvent) => void;
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
}

const ChatInput: React.FC<ChatInputProps> = ({
  input,
  setInput,
  isLoading,
  requestStartTime,
  onSendMessage,
  textareaRef
}) => {
  const [elapsed, setElapsed] = useState<number>(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading && requestStartTime) {
      setElapsed(Math.floor((Date.now() - requestStartTime) / 1000));
      interval = setInterval(() => {
        setElapsed(Math.floor((Date.now() - requestStartTime) / 1000));
      }, 1000);
    } else {
      setElapsed(0);
    }
    return () => clearInterval(interval);
  }, [isLoading, requestStartTime]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (input.trim() && !isLoading) {
        onSendMessage(e as React.FormEvent);
      }
    }
  };

  return (
    <CardFooter className="border-t pt-4">
      <form onSubmit={onSendMessage} className="flex w-full items-center space-x-2">
        <Textarea
          ref={textareaRef}
          id="message"
          placeholder="Digite sua mensagem..."
          className="flex-1 min-h-[60px] max-h-[70vh] overflow-y-auto resize-y"
          autoComplete="off"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={3}
        />
        <Button type="submit" size="icon" disabled={isLoading} className={isLoading ? "w-16" : ""}>
          {isLoading ? (
            <div className="flex items-center gap-1">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-xs">{elapsed}s</span>
            </div>
          ) : (
            <Send className="h-4 w-4" />
          )}
          <span className="sr-only">Enviar</span>
        </Button>
      </form>
    </CardFooter>
  );
};

export default ChatInput;
