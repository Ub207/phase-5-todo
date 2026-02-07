'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import TodoList from '@/components/TodoList';
import ChatInterface from '@/components/ChatInterface';
import { useAuth } from '@/contexts/AuthContext';

export default function TasksPage() {
  const router = useRouter();
  const { isAuthenticated, loading, user, logout } = useAuth();
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/');
    }
  }, [loading, isAuthenticated, router]);

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
    return null;
  }

  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Tasks
              </h1>
              <p className="text-gray-600">
                Manage your tasks with AI assistance
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600 mb-2">
                <span className="font-medium">{user?.email}</span>
              </p>
              <button
                onClick={logout}
                className="text-sm text-red-600 hover:text-red-800 underline"
              >
                Sign Out
              </button>
            </div>
          </div>

          <nav className="flex gap-4 mt-6">
            <button
              onClick={() => router.push('/')}
              className="text-gray-600 hover:text-gray-800"
            >
              ← Home
            </button>
            <button
              onClick={() => router.push('/recurring')}
              className="text-blue-600 hover:text-blue-800"
            >
              🔄 Recurring Tasks
            </button>
          </nav>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <TodoList key={refreshKey} />
          <ChatInterface onTaskCreated={handleTaskCreated} />
        </div>

        <footer className="mt-8 text-center text-sm text-gray-500">
          <p>Powered by FastAPI & Next.js 16</p>
        </footer>
      </div>
    </main>
  );
}
