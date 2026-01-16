import React from 'react';
import { ChatSession } from '../types';

interface SidebarProps {
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
  isOpen: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  isOpen,
  onCloseMobile,
}) => {
  return (
    <>
      {/* Mobile Overlay */}
      <div
        className={`fixed inset-0 z-20 bg-black/50 backdrop-blur-sm transition-opacity lg:hidden ${
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onCloseMobile}
      />

      {/* Sidebar Container */}
      <aside
        className={`fixed inset-y-0 left-0 z-30 w-72 transform bg-zinc-900 border-r border-zinc-800 transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-zinc-800">
            <button
              onClick={() => {
                onNewChat();
                onCloseMobile();
              }}
              className="flex items-center justify-center w-full px-4 py-3 text-sm font-medium text-white transition-all bg-indigo-600 rounded-lg hover:bg-indigo-500 active:scale-[0.98] shadow-lg shadow-indigo-900/20 group"
            >
              <i className="mr-2 text-lg ph ph-plus"></i>
              New Research Task
            </button>
          </div>

          {/* Session List */}
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {sessions.length === 0 && (
              <div className="p-4 text-center text-zinc-500 text-sm">
                <i className="ph ph-chats text-3xl mb-2 block opacity-50"></i>
                No history yet. Start a new research task!
              </div>
            )}

            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => {
                  onSelectSession(session.id);
                  onCloseMobile();
                }}
                className={`w-full flex items-start px-3 py-3 text-left text-sm rounded-md transition-colors group ${
                  activeSessionId === session.id
                    ? 'bg-zinc-800 text-white'
                    : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
                }`}
              >
                <i className="mt-0.5 mr-3 ph ph-chat-teardrop-text shrink-0"></i>
                <div className="truncate">
                  <div className="font-medium truncate">{session.title}</div>
                  <div className="text-xs text-zinc-500 mt-0.5">
                    {new Date(session.createdAt).toLocaleDateString()}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-zinc-800">
            <div className="flex items-center gap-3 text-zinc-400 text-sm">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-indigo-600 flex items-center justify-center text-white font-bold shadow-inner">
                RA
              </div>
              <div className="flex flex-col">
                <span className="text-white font-medium">Research Agent</span>
                <span className="text-xs text-green-500 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                  Online
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
