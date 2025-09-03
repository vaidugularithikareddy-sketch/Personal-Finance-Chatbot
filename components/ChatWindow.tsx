
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { UserType, Message, Sender } from '../types';
import { createChatSession } from '../services/geminiService';
import MessageBubble from './MessageBubble';
import UserInput from './UserInput';
import TypingIndicator from './TypingIndicator';
import type { Chat } from '@google/genai';

interface ChatWindowProps {
  userType: UserType;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ userType }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const chatRef = useRef<Chat | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const initializeChat = useCallback(async () => {
    setIsLoading(true);
    setMessages([]);
    try {
      if (!process.env.API_KEY) {
        throw new Error("API key not found.");
      }
      chatRef.current = createChatSession(userType);
      
      const welcomeStream = await chatRef.current.sendMessageStream({ message: "Hello" });
      
      const botMessageId = `bot-${Date.now()}`;
      const initialBotMessage: Message = { id: botMessageId, sender: Sender.Bot, text: '' };
      setMessages([initialBotMessage]);
      
      let currentText = '';
      for await (const chunk of welcomeStream) {
        currentText += chunk.text;
        setMessages([{ ...initialBotMessage, text: currentText }]);
      }
    } catch (error) {
       console.error("Failed to initialize chat:", error);
       const errorMessage: Message = {
           id: `error-${Date.now()}`,
           sender: Sender.Bot,
           text: "Sorry, I'm having trouble connecting. Please check your API key and try again later.",
       };
       setMessages([errorMessage]);
    } finally {
        setIsLoading(false);
    }
  }, [userType]);

  useEffect(() => {
    initializeChat();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userType]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    const userMessage: Message = { id: `user-${Date.now()}`, sender: Sender.User, text };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      if (!chatRef.current) {
        throw new Error("Chat session is not initialized.");
      }

      const stream = await chatRef.current.sendMessageStream({ message: text });
      
      const botMessageId = `bot-${Date.now()}`;
      setMessages(prev => [...prev, { id: botMessageId, sender: Sender.Bot, text: '' }]);

      let currentText = '';
      for await (const chunk of stream) {
        currentText += chunk.text;
        setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && lastMessage.id === botMessageId) {
                lastMessage.text = currentText;
            }
            return newMessages;
        });
      }

    } catch (error) {
      console.error("Failed to send message:", error);
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        sender: Sender.Bot,
        text: "I encountered an error. Please try again.",
      };
      setMessages(prev => [...prev.slice(0, -1), errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-grow p-6 overflow-y-auto space-y-4">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {isLoading && messages.length > 0 && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 border-t border-gray-200">
        <UserInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default ChatWindow;
