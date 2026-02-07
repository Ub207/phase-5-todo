'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import RecurringTasksList from '@/components/RecurringTasksList';
import RecurringTaskForm from '@/components/RecurringTaskForm';
import { useAuth } from '@/contexts/AuthContext';
import { RecurringRule } from '@/lib/api';

export default function RecurringPage() {
  const router = useRouter();
  const { isAuthenticated, loading, user, logout } = useAuth();
  const [recurringRefreshKey, setRecurringRefreshKey] = useState(0);
  const [showRecurringForm, setShowRecurringForm] = useState(false);
  const [editingRule, setEditingRule] = useState<RecurringRule | null>(null);

  useEffect(() => {
    if (!loading && !isAuthenticated) {
      router.push('/');
    }
  }, [loading, isAuthenticated, router]);

  const handleRecurringCreated = () => {
    setRecurringRefreshKey(prev => prev + 1);
    setShowRecurringForm(false);
    setEditingRule(null);
  };

  const handleEditRule = (rule: RecurringRule) => {
    setEditingRule(rule);
    setShowRecurringForm(true);
  };

  const handleCloseForm = () => {
    setShowRecurringForm(false);
    setEditingRule(null);
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
                Recurring Tasks
              </h1>
              <p className="text-gray-600">
                Set up tasks that repeat automatically
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
              onClick={() => router.push('/tasks')}
              className="text-blue-600 hover:text-blue-800"
            >
              📋 Regular Tasks
            </button>
          </nav>
        </header>

        <RecurringTasksList
          onCreateClick={() => setShowRecurringForm(true)}
          onEditClick={handleEditRule}
          refreshTrigger={recurringRefreshKey}
        />

        <footer className="mt-8 text-center text-sm text-gray-500">
          <p>Powered by FastAPI & Next.js 16</p>
        </footer>
      </div>

      {showRecurringForm && (
        <RecurringTaskForm
          onClose={handleCloseForm}
          onSuccess={handleRecurringCreated}
          editRule={editingRule}
        />
      )}
    </main>
  );
}
