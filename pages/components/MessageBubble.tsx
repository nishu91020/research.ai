import React, { useEffect } from 'react';
import { Message, Role, GroundingChunk } from '../../types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageBubbleProps {
  message: Message;
}

const cleanAndFormatText = (text: string): string => {
  console.log(text);
  // Handle JSON-encoded strings
  if (text.startsWith('"') && text.endsWith('"')) {
    try {
      text = JSON.parse(text);
    } catch {
      // Not JSON, use as-is
    }
  }
  
  // Replace escaped newlines and other escape sequences
  return text
    .replace(/\\n/g, '\n')
    .replace(/\\t/g, '\t')
    .replace(/\\r/g, '\r')
    .replace(/\\\//g, '/')
    .replace(/\\"/g, '"');
};

const markdownComponents = {
  h1: (props: any) => <h1 className="text-2xl font-bold text-white mt-6 mb-3" {...props} />,
  h2: (props: any) => <h2 className="text-xl font-semibold text-white mt-5 mb-2" {...props} />,
  h3: (props: any) => <h3 className="text-lg font-semibold text-zinc-100 mt-4 mb-2" {...props} />,
  p: (props: any) => <p className="text-zinc-200 my-2 leading-relaxed" {...props} />,
  ul: (props: any) => <ul className="list-disc list-inside space-y-1 my-2 ml-2" {...props} />,
  ol: (props: any) => <ol className="list-decimal list-inside space-y-1 my-2 ml-2" {...props} />,
  li: (props: any) => <li className="text-zinc-200 ml-2" {...props} />,
  a: (props: any) => <a className="text-indigo-400 hover:text-indigo-300 underline" target="_blank" rel="noopener noreferrer" {...props} />,
  strong: (props: any) => <strong className="text-white font-semibold" {...props} />,
  em: (props: any) => <em className="text-zinc-300 italic" {...props} />,
  code: (props: any) => <code className="bg-zinc-800 px-2 py-1 rounded text-xs text-zinc-100 font-mono" {...props} />,
  pre: (props: any) => <pre className="bg-zinc-900 p-3 rounded my-2 overflow-x-auto text-xs" {...props} />,
  blockquote: (props: any) => <blockquote className="border-l-4 border-indigo-500 pl-4 italic text-zinc-300 my-2" {...props} />,
  hr: (props: any) => <hr className="my-4 border-t border-zinc-700/50" {...props} />,
};

const SourcesList: React.FC<{ chunks: GroundingChunk[] }> = ({ chunks }) => {
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
  useEffect(()=>{
    console.log("Rendering message:", message.text);
  },[message.text])
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
                    <div className="prose prose-invert max-w-none">
                      <ReactMarkdown 
                        remarkPlugins={[remarkGfm]} 
                        components={markdownComponents}
                      >
                          {cleanAndFormatText(message.text)}
                      </ReactMarkdown>
                    </div>
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
