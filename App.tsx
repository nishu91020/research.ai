import React, { useState, useRef, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { MessageBubble } from './components/MessageBubble';
import { ChatInput } from './components/ChatInput';
import { ChatSession, Message, Role, ChatState } from './types';
import { v4 as uuidv4 } from 'uuid'; 

const generateId = () => uuidv4();

const App: React.FC = () => {
  const [chatState, setChatState] = useState<ChatState>({
    sessions: [],
    activeSessionId: null,
    isSidebarOpen: false,
  });
  
  const [isGenerating, setIsGenerating] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('research-agent-sessions');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setChatState(prev => ({
            ...prev,
            sessions: parsed,
            activeSessionId: parsed[0].id
          }));
        } else {
          createNewSession();
        }
      } catch (e) {
        createNewSession();
      }
    } else {
      createNewSession();
    }
  }, []);

  useEffect(() => {
    if (chatState.sessions.length > 0) {
      localStorage.setItem('research-agent-sessions', JSON.stringify(chatState.sessions));
    }
  }, [chatState.sessions]);

  const activeSession = chatState.sessions.find(s => s.id === chatState.activeSessionId);
  
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeSession?.messages, isGenerating]);

  const createNewSession = () => {
    const newSession: ChatSession = {
      id: generateId(),
      title: 'New Research Task',
      messages: [],
      createdAt: Date.now(),
    };

    setChatState(prev => ({
      ...prev,
      sessions: [newSession, ...prev.sessions],
      activeSessionId: newSession.id,
    }));
  };

  const handleSendMessage = async (text: string) => {
    if (!chatState.activeSessionId || isGenerating) return;

    const sessionId = chatState.activeSessionId;
    
    const userMessage: Message = {
      id: generateId(),
      role: Role.USER,
      text: text,
      timestamp: Date.now(),
    };

    setChatState(prev => {
      const updatedSessions = prev.sessions.map(session => {
        if (session.id === sessionId) {
          const title = session.messages.length === 0 ? text.slice(0, 30) + (text.length > 30 ? '...' : '') : session.title;
          return {
            ...session,
            title,
            messages: [...session.messages, userMessage]
          };
        }
        return session;
      });
      return { ...prev, sessions: updatedSessions };
    });

    setIsGenerating(true);

    const agentMsgId = generateId();
    const agentMessagePlaceholder: Message = {
      id: agentMsgId,
      role: Role.MODEL,
      text: '',
      timestamp: Date.now(),
      isStreaming: true
    };

    setChatState(prev => ({
        ...prev,
        sessions: prev.sessions.map(s => s.id === sessionId ? {
            ...s,
            messages: [...s.messages, agentMessagePlaceholder]
        } : s)
    }));

    try {
        console.log("Starting research for:", text);
        const encodedTopic = encodeURIComponent(text);
        const response = await fetch(`http://localhost:8000/research/${encodedTopic}`);
        
        if (!response.ok) {
            throw new Error(`Research failed: ${response.statusText}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        
        if (!reader) {
            throw new Error("No response body");
        }

        let buffer = "";
        let collectedText = "";
        let metadata: any = {};

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split("\n");
            buffer = lines[lines.length - 1];

            for (let i = 0; i < lines.length - 1; i++) {
                const line = lines[i].trim();
                if (!line) continue;

                try {
                    const chunk = JSON.parse(line);

                    if (chunk.type === "metadata") {
                        // Store metadata
                        metadata = {
                            field: chunk.field,
                            fetched_data: chunk.fetched_data,
                            selected_articles: chunk.selected_articles
                        };
                    } else if (chunk.type === "article") {
                        // Stream article text
                        collectedText += chunk.text;
                        setChatState(prev => ({
                            ...prev,
                            sessions: prev.sessions.map(s => {
                                if (s.id === sessionId) {
                                    const msgs = s.messages.map(m => {
                                        if (m.id === agentMsgId) {
                                            return {
                                                ...m,
                                                text: collectedText,
                                                groundingMetadata: metadata
                                            };
                                        }
                                        return m;
                                    });
                                    return { ...s, messages: msgs };
                                }
                                return s;
                            })
                        }));
                    } else if (chunk.type === "summary") {
                        // Append summary with clear separation
                        collectedText += "\n\n---\n\n## Summary\n\n" + chunk.text;
                        setChatState(prev => ({
                            ...prev,
                            sessions: prev.sessions.map(s => {
                                if (s.id === sessionId) {
                                    const msgs = s.messages.map(m => {
                                        if (m.id === agentMsgId) {
                                            return {
                                                ...m,
                                                text: collectedText,
                                                groundingMetadata: metadata
                                            };
                                        }
                                        return m;
                                    });
                                    return { ...s, messages: msgs };
                                }
                                return s;
                            })
                        }));
                    } else if (chunk.type === "error") {
                        throw new Error(chunk.message);
                    } else if (chunk.type === "complete") {
                        // Response complete, update final state
                        setChatState(prev => ({
                            ...prev,
                            sessions: prev.sessions.map(s => {
                                if (s.id === sessionId) {
                                    const msgs = s.messages.map(m => {
                                        if (m.id === agentMsgId) {
                                            return {
                                                ...m,
                                                isStreaming: false,
                                                groundingMetadata: metadata
                                            };
                                        }
                                        return m;
                                    });
                                    return { ...s, messages: msgs };
                                }
                                return s;
                            })
                        }));
                    }
                } catch (e) {
                    if (e instanceof SyntaxError) {
                        console.error("Error parsing JSON chunk:", line);
                    } else {
                        console.error("Error processing chunk:", e);
                    }
                }
            }
        }
    } catch (e) {
        console.error(e);
        setChatState(prev => ({
            ...prev,
            sessions: prev.sessions.map(s => {
                if (s.id === sessionId) {
                    const msgs = s.messages.map(m => {
                        if (m.id === agentMsgId) {
                            return {
                                ...m,
                                text: `Error: ${e instanceof Error ? e.message : String(e)}`
                            };
                        }
                        return m;
                    });
                    return { ...s, messages: msgs };
                }
                return s;
            })
        }));
    } finally {
        setIsGenerating(false);
        setChatState(prev => ({
            ...prev,
            sessions: prev.sessions.map(s => {
                if (s.id === sessionId) {
                    const msgs = s.messages.map(m => m.id === agentMsgId ? { ...m, isStreaming: false } : m);
                    return { ...s, messages: msgs };
                }
                return s;
            })
        }));
    }
  };

  return (
    <div className="flex h-screen bg-black overflow-hidden font-sans text-zinc-100">
      <Sidebar
        sessions={chatState.sessions}
        activeSessionId={chatState.activeSessionId}
        onSelectSession={(id) => {
            setChatState(prev => ({ ...prev, activeSessionId: id }));
        }}
        onNewChat={createNewSession}
        isOpen={chatState.isSidebarOpen}
        onCloseMobile={() => setChatState(prev => ({ ...prev, isSidebarOpen: false }))}
      />

      <main className="flex-1 flex flex-col min-w-0 bg-zinc-950 relative">
        {/* Header */}
        <header className="h-14 border-b border-zinc-800 flex items-center justify-between px-4 bg-zinc-900/50 backdrop-blur sticky top-0 z-10">
            <div className="flex items-center gap-3">
                <button 
                    onClick={() => setChatState(prev => ({ ...prev, isSidebarOpen: true }))}
                    className="lg:hidden p-2 text-zinc-400 hover:text-white"
                >
                    <i className="ph ph-list text-xl"></i>
                </button>
                <div className="flex items-center gap-2">
                    <span className="font-semibold text-zinc-100">Research Buddy</span>
                </div>
            </div>
        </header>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-8 custom-scrollbar">
            {activeSession ? (
                <>
                    {activeSession.messages.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-zinc-500 space-y-6 opacity-60">
                            <div className="w-20 h-20 bg-zinc-900 rounded-2xl flex items-center justify-center border border-zinc-800 shadow-xl">
                                <i className="ph ph-globe-stand text-4xl text-indigo-500"></i>
                            </div>
                            <div className="text-center max-w-md">
                                <h3 className="text-lg font-medium text-zinc-300 mb-2">Ready to Research</h3>
                                <p className="text-sm">Ask me to find information, compare products, or summarize recent events. I use Google Search to find the latest data.</p>
                            </div>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                                {["Latest advancements in fusion energy", "Compare iPhone 15 Pro vs Pixel 9 Pro", "Summary of yesterday's stock market", "Who won the 2024 Super Bowl?"].map(q => (
                                    <button 
                                        key={q} 
                                        onClick={() => handleSendMessage(q)}
                                        className="text-xs p-3 bg-zinc-900 border border-zinc-800 rounded hover:border-indigo-700 hover:bg-zinc-800 transition-all text-left"
                                    >
                                        "{q}"
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}
                    <div className="max-w-3xl mx-auto">
                        {activeSession.messages.map(msg => (
                            <MessageBubble key={msg.id} message={msg} />
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                </>
            ) : (
                <div className="h-full flex items-center justify-center">Loading...</div>
            )}
        </div>

        {/* Input Area */}
        <ChatInput onSendMessage={handleSendMessage} disabled={isGenerating} />
      </main>
    </div>
  );
};

export default App;
