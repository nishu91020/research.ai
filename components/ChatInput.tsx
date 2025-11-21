import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
  onSendMessage: (text: string) => void;
  disabled: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSend = () => {
    if (!input.trim() || disabled) return;
    onSendMessage(input.trim());
    setInput('');
    // Reset height
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full bg-zinc-900/80 backdrop-blur-xl border-t border-zinc-800 p-4">
      <div className="max-w-3xl mx-auto relative flex items-end gap-2 bg-zinc-800/50 p-2 rounded-xl border border-zinc-700 focus-within:border-zinc-600 focus-within:ring-1 focus-within:ring-zinc-600 transition-all shadow-sm">
        
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={disabled ? "Research Agent is thinking..." : "Ask anything. I'll research it for you..."}
          className="w-full bg-transparent text-zinc-200 placeholder-zinc-500 text-sm px-3 py-3 focus:outline-none resize-none max-h-32 overflow-y-auto custom-scrollbar"
          rows={1}
        />

        <div className="flex pb-1.5 pr-1.5">
            <button
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            className={`p-2 rounded-lg transition-all flex items-center justify-center ${
                input.trim() && !disabled
                ? 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-lg shadow-indigo-900/30'
                : 'bg-zinc-700 text-zinc-500 cursor-not-allowed'
            }`}
            >
            {disabled ? (
                <i className="ph ph-spinner animate-spin text-lg"></i>
            ) : (
                <i className="ph ph-paper-plane-right text-lg"></i>
            )}
            </button>
        </div>
      </div>
      <div className="max-w-3xl mx-auto mt-2 text-center">
        <p className="text-[10px] text-zinc-500">
            <i className="ph ph-info mr-1 align-middle"></i>
            Research Agent uses GPT-4o & Google Search. Citations are provided for verification.
        </p>
      </div>
    </div>
  );
};
