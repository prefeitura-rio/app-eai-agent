import React from 'react';
import { CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Loader2, Send } from 'lucide-react';

interface ChatInputProps {
  input: string;
  setInput: (value: string) => void;
  isLoading: boolean;
  onSendMessage: (e: React.FormEvent) => void;
  textareaRef: React.RefObject<HTMLTextAreaElement | null>;
}

const ChatInput: React.FC<ChatInputProps> = ({
  input,
  setInput,
  isLoading,
  onSendMessage,
  textareaRef
}) => {
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
          className="flex-1 min-h-[60px] resize-none"
          autoComplete="off"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
          rows={3}
          style={{ resize: 'none' }}
        />
        <Button type="submit" size="icon" disabled={isLoading}>
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
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
