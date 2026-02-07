'use client';

import { useState } from 'react';
import { chatApi, taskApi } from '@/lib/api';

interface Message {
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  onTaskCreated?: () => void;
}

export default function ChatInterface({ onTaskCreated }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = input;
    setInput('');
    setLoading(true);

    try {
      // Try to send message to chat API
      const response = await chatApi.sendMessage(userInput);

      const aiMessage: Message = {
        type: 'ai',
        content: response.response || 'Message processed!',
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);

      // If a task was created, notify parent to refresh
      if (response.task_created && onTaskCreated) {
        onTaskCreated();
      }
    } catch (err: any) {
      // If chat fails, try to create as simple task
      try {
        // Parse simple task creation patterns
        const task = await taskApi.createTask({
          title: userInput,
          priority: 'medium',
        });

        const aiMessage: Message = {
          type: 'ai',
          content: `Task created: "${task.title}"`,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, aiMessage]);

        if (onTaskCreated) {
          onTaskCreated();
        }
      } catch (createErr: any) {
        const errorMessage: Message = {
          type: 'ai',
          content: createErr.response?.data?.detail || 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex flex-col h-[600px]">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">AI Todo Assistant</h2>

      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 italic mt-8">
            <p>Start chatting with your AI assistant!</p>
            <p className="text-sm mt-2">
              Try: "Add a task to buy groceries" or "Create a high priority task to call mom"
            </p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  msg.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                <p className="text-xs mt-1 opacity-70">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-800"
          disabled={loading}
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
        >
          Send
        </button>
      </div>
    </div>
  );
}
