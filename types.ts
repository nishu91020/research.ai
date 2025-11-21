export enum Role {
  USER = 'user',
  MODEL = 'model'
}

export interface GroundingChunk {
  web?: {
    uri: string;
    title: string;
  };
}

export interface GroundingMetadata {
  groundingChunks?: GroundingChunk[];
  groundingSupports?: any[];
  searchEntryPoint?: any;
}

export interface Message {
  id: string;
  role: Role;
  text: string;
  timestamp: number;
  isStreaming?: boolean;
  groundingMetadata?: GroundingMetadata | null;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
}

export interface ChatState {
  sessions: ChatSession[];
  activeSessionId: string | null;
  isSidebarOpen: boolean;
}
