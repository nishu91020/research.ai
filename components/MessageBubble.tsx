import React from 'react';
import { Message, Role, GroundingChunk } from '../types';

interface MessageBubbleProps {
  message: Message;
}

const FormattedText: React.FC<{ text: string }> = ({ text }) => {
  // Simple parser to handle newlines and basic bolding for lack of a full MD library
  // In a real production app, use 'react-markdown'
  return (
    <div className="prose prose-invert prose-sm max-w-none leading-relaxed text-zinc-300">
      {text.split('\n').map((line, i) => {
        if (line.trim() === '') return <br key={i} className="h-2 block" />;
        
        // Basic bold parsing (**text**)
        const parts = line.split(/(\*\*.*?\*\*)/g);
        return (
          <div key={i} className="min-h-[1.5em]">
            {parts.map((part, j) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={j} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
              }
              return <span key={j}>{part}</span>;
            })}
          </div>
        );
      })}
    </div>
  );
};

const SourcesList: React.FC<{ chunks: GroundingChunk[] }> = ({ chunks }) => {
  // Filter out chunks that don't have web URIs
  const sources = chunks.filter(c => c.web?.uri);

  if (sources.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-zinc-800/50">
      <div className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-2 flex items-center gap-1">
        <i className="ph ph-globe-hemisphere-west"></i>
        Sources Found
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {sources.map((source, idx) => (
          <a
            key={idx}
            href={source.web?.uri}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center p-2 bg-zinc-900/50 hover:bg-zinc-800 border border-zinc-800 hover:border-zinc-700 rounded text-xs transition-colors group"
          >
            <div className="w-5 h-5 flex items-center justify-center bg-zinc-800 rounded-full text-zinc-400 group-hover:text-indigo-400 shrink-0 mr-2">
              <span className="font-mono text-[10px]">{idx + 1}</span>
            </div>
            <div className="truncate text-zinc-400 group-hover:text-indigo-300">
              {source.web?.title || "Unknown Source"}
            </div>
            <i className="ph ph-arrow-square-out ml-auto text-zinc-600 group-hover:text-indigo-400"></i>
          </a>
        ))}
      </div>
    </div>
  );
};

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === Role.USER;

  return (
    <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`flex max-w-4xl w-full gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        
        {/* Avatar */}
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-lg ${
          isUser 
            ? 'bg-zinc-700 text-white' 
            : 'bg-indigo-600 text-white'
        }`}>
          <i className={`text-sm ph ${isUser ? 'ph-user' : 'ph-robot'}`}></i>
        </div>

        {/* Content Bubble */}
        <div className={`flex-1 min-w-0`}>
            <div className={`flex items-center gap-2 mb-1 ${isUser ? 'justify-end' : 'justify-start'}`}>
                <span className="text-xs font-medium text-zinc-500">
                    {isUser ? 'You' : 'Research Agent'}
                </span>
                <span className="text-[10px] text-zinc-600">
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
            </div>

            <div className={`p-4 rounded-2xl shadow-sm ${
                isUser 
                ? 'bg-zinc-800 text-zinc-100 rounded-tr-none border border-zinc-700' 
                : 'bg-gradient-to-b from-zinc-900 to-zinc-900/95 text-zinc-100 rounded-tl-none border border-zinc-800/60'
            }`}>
                {message.text ? (
                    <FormattedText text={message.text} />
                ) : (
                    // Loading Pulse
                    <div className="flex items-center gap-1 h-6">
                        <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                        <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                        <span className="w-1.5 h-1.5 bg-zinc-500 rounded-full animate-bounce"></span>
                    </div>
                )}

                {/* Render Sources if Agent */}
                {!isUser && message.groundingMetadata?.groundingChunks && (
                    <SourcesList chunks={message.groundingMetadata.groundingChunks} />
                )}
            </div>
        </div>
      </div>
    </div>
  );
};
