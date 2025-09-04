import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Chat } from '@google/genai';
import type { GenerateContentParameters } from '@google/genai';
import type { Message, Source } from './types';
import { Persona } from './types';
import { createChat } from './services/geminiService';
import PersonaSelector from './components/PersonaSelector';
import ChatWindow from './components/ChatWindow';
import { BotIcon } from './components/icons';

const App: React.FC = () => {
  const [persona, setPersona] = useState<Persona>(Persona.STUDENT);
  const [chat, setChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [useWebSearch, setUseWebSearch] = useState<boolean>(false);
  const isInitializing = useRef(true);

  const initializeChat = useCallback(() => {
    setIsLoading(true);
    setMessages([]);
    const newChat = createChat(persona);
    setChat(newChat);

    const welcomeMessage: Message = {
      id: `bot-welcome-${Date.now()}`,
      sender: 'bot',
      text: `Hello! I'm your personal finance advisor. As a ${persona.toLowerCase()}, what financial questions do you have for me today? Feel free to ask about savings, investments, taxes, or even ask me to analyze your budget.`,
    };
    
    setMessages([welcomeMessage]);
    setIsLoading(false);
    isInitializing.current = false;
  }, [persona]);

  useEffect(() => {
    initializeChat();
  }, [initializeChat]);


  const handleSendMessage = async (userInput: string, webSearchEnabled: boolean) => {
    if (!userInput.trim() || isLoading || !chat) return;

    setIsLoading(true);
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: userInput,
    };
    setMessages(prev => [...prev, userMessage]);

    const botMessageId = `bot-${Date.now()}`;
    setMessages(prev => [...prev, { id: botMessageId, sender: 'bot', text: '' }]);

    try {
       const request: GenerateContentParameters = {
        contents: [{ parts: [{ text: userInput }] }],
      };

      if (webSearchEnabled) {
        request.config = {
          tools: [{ googleSearch: {} }],
        };
      }

      const stream = await chat.sendMessageStream(request);
      
      let fullResponse = '';
      let sources: Source[] | undefined = undefined;

      for await (const chunk of stream) {
        fullResponse += chunk.text;
        
        const newSources = chunk.candidates?.[0]?.groundingMetadata?.groundingChunks
            ?.map(c => ({ uri: c.web.uri, title: c.web.title }))
            .filter(s => s.uri);

        if (newSources && newSources.length > 0) {
            if (!sources) sources = [];
            newSources.forEach(newSource => {
                if (!sources.find(existing => existing.uri === newSource.uri)) {
                    sources.push(newSource);
                }
            })
        }

        setMessages(prev =>
          prev.map(msg =>
            msg.id === botMessageId ? { ...msg, text: fullResponse, sources } : msg
          )
        );
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === botMessageId ? { ...msg, text: 'Sorry, I encountered an error. Please try again.' } : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };
  
  const handlePersonaChange = (newPersona: Persona) => {
    if (newPersona !== persona) {
        setPersona(newPersona);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-slate-900 text-white font-sans">
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-slate-700 p-4 shadow-lg z-10">
        <div className="container mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3">
            <BotIcon className="w-8 h-8 text-cyan-400" />
            <h1 className="text-xl font-bold text-slate-200">Personal Finance Chatbot</h1>
          </div>
          <PersonaSelector currentPersona={persona} onPersonaChange={handlePersonaChange} />
        </div>
      </header>

      <main className="flex-1 container mx-auto w-full max-w-4xl p-4 overflow-y-auto">
        {isInitializing.current ? (
             <div className="flex items-center justify-center h-full">
                <p className="text-slate-400">Initializing chatbot for {persona}...</p>
             </div>
        ) : (
            <ChatWindow
                messages={messages}
                isLoading={isLoading}
                onSendMessage={handleSendMessage}
                useWebSearch={useWebSearch}
                onWebSearchChange={setUseWebSearch}
            />
        )}
      </main>
    </div>
  );
};

export default App;

import React, { useState, useRef, useEffect } from 'react';
import type { Message } from '../types';
import MessageBubble from './MessageBubble';
import { SendIcon } from './icons';

interface ChatWindowProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (message: string, useWebSearch: boolean) => void;
  useWebSearch: boolean;
  onWebSearchChange: (value: boolean) => void;
}

const TypingIndicator: React.FC = () => (
  <div className="flex items-center space-x-1 p-3">
    <span className="text-slate-400 text-sm">Advisor is typing</span>
    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce"></div>
  </div>
);

const WebSearchToggle: React.FC<{ enabled: boolean; onChange: (enabled: boolean) => void, disabled: boolean }> = ({ enabled, onChange, disabled }) => {
  return (
    <button
      type="button"
      onClick={() => onChange(!enabled)}
      className="flex items-center gap-2 text-sm text-slate-400 hover:text-slate-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      aria-pressed={enabled}
      disabled={disabled}
    >
      <div className={`w-10 h-5 flex items-center rounded-full p-0.5 transition-colors duration-300 ${enabled ? 'bg-cyan-600' : 'bg-slate-700'}`}>
        <div className={`w-4 h-4 bg-white rounded-full shadow-md transform transition-transform duration-300 ${enabled ? 'translate-x-5' : 'translate-x-0'}`} />
      </div>
      <span>Search the web</span>
    </button>
  );
};


const ChatWindow: React.FC<ChatWindowProps> = ({ messages, isLoading, onSendMessage, useWebSearch, onWebSearchChange }) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSendMessage(input, useWebSearch);
    setInput('');
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 space-y-6 overflow-y-auto pr-2">
        {messages.map((msg, index) => (
          <MessageBubble key={msg.id} message={msg} isStreaming={isLoading && index === messages.length -1} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="mt-6">
        {isLoading && <TypingIndicator />}
        <form onSubmit={handleSubmit}>
          <div className="relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a financial question..."
              disabled={isLoading}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg py-3 pl-4 pr-14 text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-shadow duration-300"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 p-2 rounded-full text-slate-400 bg-slate-700 hover:bg-cyan-600 hover:text-white transition-colors duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <SendIcon className="w-5 h-5" />
            </button>
          </div>
          <div className="flex justify-end pt-2 pr-1">
             <WebSearchToggle enabled={useWebSearch} onChange={onWebSearchChange} disabled={isLoading} />
          </div>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow;

import React from 'react';

export const BotIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path fillRule="evenodd" d="M4.5 3.75a3 3 0 00-3 3v10.5a3 3 0 003 3h15a3 3 0 003-3V6.75a3 3 0 00-3-3h-15zm4.125 3a.75.75 0 000 1.5h6.75a.75.75 0 000-1.5h-6.75zm0 3.75a.75.75 0 000 1.5h6.75a.75.75 0 000-1.5h-6.75zm0 3.75a.75.75 0 000 1.5h4.5a.75.75 0 000-1.5h-4.5z" clipRule="evenodd" />
  </svg>
);

export const UserIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clipRule="evenodd" />
  </svg>
);

export const SendIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" {...props}>
    <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
  </svg>
);

export const ExternalLinkIcon: React.FC<React.SVGProps<SVGSVGElement>> = (props) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" {...props}>
        <path d="M12.232 4.232a2.5 2.5 0 013.536 3.536l-1.225 1.224a.75.75 0 001.061 1.06l1.224-1.224a4 4 0 00-5.656-5.656l-3 3a4 4 0 00.225 5.865.75.75 0 00.977-1.138 2.5 2.5 0 01-.142-3.665l3-3z" />
        <path d="M8.603 14.53a2.5 2.5 0 01-3.535 0l-1.225-1.225a.75.75 0 00-1.061 1.06l1.225 1.224a4 4 0 005.656 0l3-3a4 4 0 00-.225-5.865.75.75 0 00-.977 1.138 2.5 2.5 0 01.142 3.665l-3 3z" />
    </svg>
);

import React from 'react';
import type { Message } from '../types';
import { BotIcon, UserIcon, ExternalLinkIcon } from './icons';

interface MessageBubbleProps {
  message: Message;
  isStreaming: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isStreaming }) => {
  const isBot = message.sender === 'bot';

  return (
    <div className={`flex items-start gap-4 ${!isBot ? 'flex-row-reverse' : ''}`}>
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isBot ? 'bg-slate-700' : 'bg-cyan-700'}`}>
        {isBot ? <BotIcon className="w-6 h-6 text-cyan-400" /> : <UserIcon className="w-6 h-6 text-slate-200" />}
      </div>
      <div
        className={`w-full max-w-xl rounded-lg px-5 py-3 shadow-md ${
          isBot ? 'bg-slate-800 text-slate-300 rounded-tl-none' : 'bg-cyan-600 text-white rounded-tr-none'
        }`}
      >
        <p className="whitespace-pre-wrap">
            {message.text}
            {isStreaming && <span className="inline-block w-2 h-4 bg-slate-300 ml-1 animate-pulse" />}
        </p>
         {message.sources && message.sources.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-700">
            <h4 className="text-xs font-semibold text-slate-400 mb-2">SOURCES</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {message.sources.map((source) => (
                <a
                  key={source.uri}
                  href={source.uri}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="bg-slate-700/50 hover:bg-slate-700 p-2 rounded-md text-sm text-slate-300 truncate transition-colors duration-200 flex items-center gap-2"
                  title={source.title}
                >
                  <ExternalLinkIcon className="w-4 h-4 flex-shrink-0 text-slate-500"/>
                  <span className="truncate">{source.title || new URL(source.uri).hostname}</span>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;

import React from 'react';
import { Persona } from '../types';

interface PersonaSelectorProps {
  currentPersona: Persona;
  onPersonaChange: (persona: Persona) => void;
}

const PersonaSelector: React.FC<PersonaSelectorProps> = ({ currentPersona, onPersonaChange }) => {
  const personas = [Persona.STUDENT, Persona.PROFESSIONAL];

  return (
    <div className="flex bg-slate-700 rounded-lg p-1">
      {personas.map(persona => (
        <button
          key={persona}
          onClick={() => onPersonaChange(persona)}
          className={`px-4 py-1.5 text-sm font-semibold rounded-md transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-800 focus:ring-cyan-500 ${
            currentPersona === persona
              ? 'bg-cyan-600 text-white shadow-md'
              : 'text-slate-300 hover:bg-slate-600/50'
          }`}
        >
          I am a {persona}
        </button>
      ))}
    </div>
  );
};

export default PersonaSelector;

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Personal Finance Chatbot</title>
    <script src="https://cdn.tailwindcss.com"></script>
  <script type="importmap">
{
  "imports": {
    "react/": "https://aistudiocdn.com/react@^19.1.1/",
    "react": "https://aistudiocdn.com/react@^19.1.1",
    "react-dom/": "https://aistudiocdn.com/react-dom@^19.1.1/",
    "@google/genai": "https://aistudiocdn.com/@google/genai@^1.16.0"
  }
}
</script>
</head>
  <body class="bg-slate-900">
    <div id="root"></div>
    <script type="module" src="/index.tsx"></script>
  </body>
</html>

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

{
  "name": "Copy of Personal Finance Chatbot",
  "description": "An intelligent conversational AI that provides personalized financial guidance on savings, taxes, and investments. It adapts its tone and complexity for students and professionals to help improve financial literacy.",
  "requestFramePermissions": []
}

import { GoogleGenAI, Chat } from "@google/genai";
import { Persona } from '../types';

const getSystemInstruction = (persona: Persona): string => {
    if (persona === Persona.STUDENT) {
        return `You are a friendly, encouraging financial advisor chatbot designed for students.
- Your primary goal is to make finance approachable and easy to understand.
- Use simple, clear language and avoid complex jargon. If you must use a financial term, explain it immediately.
- Use relatable examples for students (e.g., part-time jobs, student loans, saving for spring break).
- Focus on foundational topics: budgeting, saving money, understanding credit, dealing with student debt, and getting started with small, low-risk investments.
- Keep your tone positive and supportive. Frame advice as actionable steps.
- When asked to analyze a budget, be gentle and focus on small, achievable changes.
- Do not give any investment advice that is not factual or educational in nature.`;
    }
    
    return `You are an expert, data-driven financial advisor chatbot for working professionals.
- Your tone should be professional, insightful, and precise.
- You can confidently use financial terminology (e.g., asset allocation, tax-loss harvesting, diversification).
- Focus on more advanced topics: retirement planning (401k, IRA, Roth IRA), tax optimization strategies, real estate, portfolio management, and wealth-building.
- Provide detailed, analytical advice supported by logical reasoning.
- When asked to analyze a budget, be thorough and identify key opportunities for optimization in savings, investments, and tax efficiency.
- You can discuss market trends and different investment vehicles in detail.
- Do not give any investment advice that is not factual or educational in nature.`;
};

export const createChat = (persona: Persona): Chat => {
    if (!process.env.API_KEY) {
        throw new Error("API_KEY environment variable not set.");
    }
    const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
    
    const systemInstruction = getSystemInstruction(persona);

    return ai.chats.create({
        model: 'gemini-2.5-flash',
        config: {
            systemInstruction,
            temperature: 0.7,
            topP: 0.9,
        },
    });
};
export enum Persona {
  STUDENT = 'Student',
  PROFESSIONAL = 'Professional',
}

export interface Source {
  uri: string;
  title: string;
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  sources?: Source[];
}
