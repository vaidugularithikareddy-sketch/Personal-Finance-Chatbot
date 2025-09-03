
import { GoogleGenAI, Chat } from "@google/genai";
import { SYSTEM_INSTRUCTIONS } from '../constants';
import { UserType } from '../types';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });

export const createChatSession = (userType: UserType): Chat => {
  const systemInstruction = SYSTEM_INSTRUCTIONS[userType];
  
  const chat = ai.chats.create({
    model: 'gemini-2.5-flash',
    config: {
      systemInstruction,
    },
  });
  
  return chat;
};
