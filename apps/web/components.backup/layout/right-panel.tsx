'use client';

import * as React from 'react';
import { useAppStore } from '@/lib/store';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Separator } from '@/components/ui/separator';
import { Send, Sparkles, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { formatDate } from '@/lib/utils';

export function RightPanel() {
  const { chatMessages, addChatMessage, clearChat } = useAppStore();
  const [input, setInput] = React.useState('');
  const scrollRef = React.useRef<HTMLDivElement>(null);

  const handleSend = () => {
    if (!input.trim()) return;

    addChatMessage({
      role: 'user',
      content: input,
    });

    setInput('');

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      addChatMessage({
        role: 'assistant',
        content: 'I can help you create and modify dashboards. What would you like to do?',
      });
    }, 500);
  };

  React.useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  return (
    <div className="h-full flex flex-col bg-background">
      {/* Header */}
      <div className="h-14 border-b border-border px-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          <span className="font-semibold">Assistant</span>
        </div>
        {chatMessages.length > 0 && (
          <Button variant="ghost" size="icon" onClick={clearChat} className="h-8 w-8">
            <Trash2 className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {chatMessages.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              <Sparkles className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p className="text-sm">Start a conversation to create or modify dashboards</p>
              <p className="text-xs mt-2">Try asking:</p>
              <ul className="text-xs mt-2 space-y-1">
                <li>&ldquo;Show me top 10 products by revenue&rdquo;</li>
                <li>&ldquo;Create a dashboard for user engagement&rdquo;</li>
                <li>&ldquo;Add a chart showing daily active users&rdquo;</li>
              </ul>
            </div>
          ) : (
            chatMessages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  'flex gap-3',
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                )}
              >
                <div
                  className={cn(
                    'max-w-[85%] rounded-lg px-3 py-2',
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground'
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p className="text-xs opacity-70 mt-1">{formatDate(message.timestamp)}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="border-t border-border p-4">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask me anything..."
            className="flex-1"
          />
          <Button onClick={handleSend} disabled={!input.trim()} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
