
import React from 'react';

interface HeaderProps {
    onReset: () => void;
    showReset: boolean;
}

const Header: React.FC<HeaderProps> = ({ onReset, showReset }) => {
  return (
    <header className="py-4 px-8 bg-white shadow-md">
      <div className="flex justify-between items-center">
        <div className="flex items-center space-x-3">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" /><path d="M13 7h-2v6h2V7zm0 8h-2v2h2v-2z" />
            </svg>
            <h1 className="text-2xl font-bold text-gray-800">FinBot</h1>
            <span className="text-sm text-gray-500 mt-1">Your Personal Finance Assistant</span>
        </div>
        {showReset && (
             <button
                onClick={onReset}
                className="px-4 py-2 text-sm font-medium text-white bg-red-500 rounded-lg hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition duration-150 ease-in-out"
            >
                Start Over
            </button>
        )}
      </div>
    </header>
  );
};

export default Header;
