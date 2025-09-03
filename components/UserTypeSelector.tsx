
import React from 'react';
import { UserType } from '../types';

interface UserTypeSelectorProps {
  onSelectUserType: (type: UserType) => void;
}

const UserCard: React.FC<{ title: string; description: string; icon: JSX.Element; onClick: () => void; }> = ({ title, description, icon, onClick }) => (
    <button
        onClick={onClick}
        className="flex flex-col items-center justify-center p-8 text-center bg-white border-2 border-gray-200 rounded-lg shadow-sm hover:border-blue-500 hover:shadow-lg transition-all duration-300 ease-in-out transform hover:-translate-y-1 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
    >
        <div className="mb-4 text-blue-500">{icon}</div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
    </button>
);


const UserTypeSelector: React.FC<UserTypeSelectorProps> = ({ onSelectUserType }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center bg-gray-50 rounded-b-2xl">
      <h2 className="text-3xl font-bold text-gray-800 mb-4">Welcome to FinBot!</h2>
      <p className="text-lg text-gray-600 mb-12 max-w-2xl">To give you the best financial advice, please tell us a little about yourself. Select the profile that best describes you.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-3xl">
        <UserCard 
            title="I'm a Student"
            description="Guidance on budgeting, saving, student loans, and building credit."
            icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" viewBox="0 0 20 20" fill="currentColor"><path d="M10.394 2.08a1 1 0 00-.788 0l-7 3.5a1 1 0 00.02 1.84L5 8.28V14a1 1 0 001 1h8a1 1 0 001-1V8.28l1.372-.68a1 1 0 00.02-1.84l-7-3.5zM6 14v-4.52l4 2v4.52H6zM14 9.28L10 11.28l-4-2V6.72l4-2l4 2v2.56z" /></svg>}
            onClick={() => onSelectUserType(UserType.Student)}
        />
        <UserCard
            title="I'm a Professional"
            description="Insights on investing, tax optimization, mortgages, and retirement planning."
            icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" viewBox="0 0 20 20" fill="currentColor"><path fillRule="evenodd" d="M6 6V5a3 3 0 013-3h2a3 3 0 013 3v1h2a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2h2zm5-1a1 1 0 00-1-1H9a1 1 0 00-1 1v1h4V5z" clipRule="evenodd" /></svg>}
            onClick={() => onSelectUserType(UserType.Professional)}
        />
      </div>
    </div>
  );
};

export default UserTypeSelector;
