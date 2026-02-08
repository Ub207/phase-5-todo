'use client';

import { useState } from 'react';
import ChatInterface from '@/components/ChatInterface';
import AuthForm from '@/components/AuthForm';
import { useAuth } from '@/contexts/AuthContext';

export default function ChatPage() {
  const { isAuthenticated, loading, user, logout } = useAuth();
  const [refreshKey, setRefreshKey] = useState(0);

  const handleTaskCreated = () => {
    setRefreshKey(prev => prev + 1);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthForm />;
  }

  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-3xl mx-auto">
        <header className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                AI Chat
              </h1>
              <p className="text-gray-600">
                Chat with AI to manage your tasks
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600 mb-2">
                Welcome, <span className="font-medium">{user?.email}</span>
              </p>
              <a href="/" className="text-sm text-blue-600 hover:text-blue-800 underline mr-4">
                Back to Dashboard
              </a>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-800 underline"
              >
                Sign Out
              </button>
            </div>
          </div>
        </header>

        <ChatInterface onTaskCreated={handleTaskCreated} />
      </div>
    </main>
  );
}
