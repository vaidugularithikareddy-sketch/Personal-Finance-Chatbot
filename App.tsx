
import React, { useState } from 'react';
import { UserType } from './types';
import UserTypeSelector from './components/UserTypeSelector';
import ChatWindow from './components/ChatWindow';
import Header from './components/Header';

const App: React.FC = () => {
  const [userType, setUserType] = useState<UserType | null>(null);

  const handleSelectUserType = (type: UserType) => {
    setUserType(type);
  };
  
  const handleReset = () => {
    setUserType(null);
  }

  return (
    <div className="flex flex-col h-screen antialiased text-gray-800">
      <Header onReset={handleReset} showReset={!!userType} />
      <main className="flex-grow flex items-center justify-center p-4 bg-gray-100">
        <div className="w-full max-w-4xl h-full max-h-[90vh] bg-white rounded-2xl shadow-xl flex flex-col">
          {!userType ? (
            <UserTypeSelector onSelectUserType={handleSelectUserType} />
          ) : (
            <ChatWindow userType={userType} />
          )}
        </div>
      </main>
    </div>
  );
};

export default App;
