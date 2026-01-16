import { GoogleGenAI, Chat, GenerateContentResponse } from "@google/genai";
import { Message, Role } from "../../types";

// Initialize the client with the environment key
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const SYSTEM_INSTRUCTION = `You are an advanced Research Agent. 
Your goal is to provide comprehensive, accurate, and well-structured answers by compiling information from various sources.
Always use the Google Search tool to verify facts and gather recent data.
Format your response using Markdown. Use headers, bullet points, and bold text for readability.
If you use search results, the system will automatically attach the citations, so focus on synthesizing the content seamlessly.`;

export class GeminiService {
  private chat: Chat | null = null;
  private modelId = "gemini-2.5-flash"; // Good balance of speed and search capability

  constructor() {
    this.initChat();
  }

  private initChat() {
    this.chat = ai.chats.create({
      model: this.modelId,
      config: {
        systemInstruction: SYSTEM_INSTRUCTION,
        tools: [{ googleSearch: {} }], // Enable Search Grounding
      },
    });
  }

  /**
   * Sends a message and yields chunks of text as they arrive.
   * Also returns grounding metadata in the final chunk if available.
   */
  async *streamMessage(
    message: string, 
    previousHistory: Message[]
  ): AsyncGenerator<{ text: string; groundingMetadata?: any }> {
    
    // If we were building a stateless service, we would rebuild history here using 'history' param.
    // For this demo, we assume the instance maintains the chat session or we re-init if needed.
    if (!this.chat) {
      this.initChat();
    }

    try {
      const resultStream = await this.chat!.sendMessageStream({ message });
      
      let collectedText = "";

      for await (const chunk of resultStream) {
        const responseChunk = chunk as GenerateContentResponse;
        const text = responseChunk.text || "";
        collectedText += text;
        
        // Check for grounding metadata in the chunk (usually appears in the candidates)
        const groundingMetadata = responseChunk.candidates?.[0]?.groundingMetadata;

        yield { 
          text: collectedText, 
          groundingMetadata: groundingMetadata 
        };
      }
    } catch (error) {
      console.error("Gemini Service Error:", error);
      yield { text: "An error occurred while connecting to the research agent. Please try again." };
    }
  }

  /**
   * Reset the chat session (context)
   */
  resetSession() {
    this.initChat();
  }
}

export const geminiService = new GeminiService();
