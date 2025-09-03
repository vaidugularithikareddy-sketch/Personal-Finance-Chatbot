
import React from 'react';
import { Message, Sender } from '../types';

interface MessageBubbleProps {
  message: Message;
}

const UserAvatar: React.FC = () => (
    <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-500 text-white font-bold flex-shrink-0">
        You
    </div>
);

const BotAvatar: React.FC = () => (
    <div className="flex items-center justify-center h-10 w-10 rounded-full bg-gray-700 text-white flex-shrink-0">
      <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
      </svg>
    </div>
);


const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.sender === Sender.User;

  return (
    <div className={`flex items-end gap-3 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && <BotAvatar />}
      <div className={`px-4 py-3 rounded-2xl max-w-lg lg:max-w-xl xl:max-w-2xl ${isUser ? 'bg-blue-600 text-white rounded-br-none' : 'bg-gray-200 text-gray-800 rounded-bl-none'}`}>
        <p className="text-sm whitespace-pre-wrap">{message.text}</p>
      </div>
       {isUser && <UserAvatar />}
    </div>
  );
};

export default MessageBubble;
