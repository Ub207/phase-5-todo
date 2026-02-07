/**
 * Frontend WebSocket Integration Example
 * Copy this code into your React/Next.js frontend for real-time task updates
 */

// ===========================
// 1. WebSocket Hook (React)
// ===========================

import { useEffect, useState, useCallback, useRef } from 'react';

/**
 * Custom hook for WebSocket connection with automatic reconnection
 * @param {string} url - WebSocket URL
 * @param {string} token - JWT authentication token
 * @returns {object} - { send, lastMessage, readyState }
 */
export function useWebSocket(url, token) {
  const [lastMessage, setLastMessage] = useState(null);
  const [readyState, setReadyState] = useState('CONNECTING');
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connect = useCallback(() => {
    try {
      // Add token as query parameter
      const wsUrl = token ? `${url}?token=${token}` : url;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('✅ WebSocket connected');
        setReadyState('OPEN');
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('📩 WebSocket message:', message);
          setLastMessage(message);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        setReadyState('ERROR');
      };

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected');
        setReadyState('CLOSED');

        // Attempt to reconnect after 3 seconds
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('🔄 Reconnecting WebSocket...');
          connect();
        }, 3000);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setReadyState('ERROR');
    }
  }, [url, token]);

  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  // Send function
  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === 'string' ? data : JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  // Ping/pong for keepalive
  useEffect(() => {
    const interval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send('ping');
      }
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return { send, lastMessage, readyState };
}


// ===========================
// 2. Usage Example (React Component)
// ===========================

export function TaskListWithRealtime() {
  const [tasks, setTasks] = useState([]);
  const token = localStorage.getItem('token'); // Get JWT token

  // Connect to WebSocket
  const { lastMessage, readyState } = useWebSocket(
    'ws://localhost:8000/ws/tasks',
    token
  );

  // Handle WebSocket messages
  useEffect(() => {
    if (!lastMessage) return;

    switch (lastMessage.type) {
      case 'task_created':
        console.log('➕ New task created:', lastMessage.data);
        // Add task to the list
        setTasks(prev => [lastMessage.data, ...prev]);
        // Optional: Show notification
        showNotification('New task created!', lastMessage.data.title);
        break;

      case 'task_completed':
        console.log('✅ Task completed:', lastMessage.data);
        // Update task in the list
        setTasks(prev => prev.map(task =>
          task.id === lastMessage.data.id
            ? { ...task, completed: true, completed_at: lastMessage.data.completed_at }
            : task
        ));
        // Optional: Show notification
        showNotification('Task completed!', lastMessage.data.title);
        break;

      case 'task_updated':
        console.log('📝 Task updated:', lastMessage.data);
        // Update task in the list
        setTasks(prev => prev.map(task =>
          task.id === lastMessage.data.id ? { ...task, ...lastMessage.data } : task
        ));
        break;

      case 'task_deleted':
        console.log('🗑️ Task deleted:', lastMessage.data);
        // Remove task from the list
        setTasks(prev => prev.filter(task => task.id !== lastMessage.data.id));
        break;

      case 'connected':
        console.log('🔗 WebSocket connection established');
        break;

      case 'pong':
        // Keepalive response
        break;

      default:
        console.log('Unknown message type:', lastMessage.type);
    }
  }, [lastMessage]);

  // Fetch initial tasks on mount
  useEffect(() => {
    async function fetchTasks() {
      try {
        const response = await fetch('http://localhost:8000/api/tasks', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        const data = await response.json();
        setTasks(data);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      }
    }

    fetchTasks();
  }, [token]);

  return (
    <div>
      <div className="status-bar">
        WebSocket: {readyState === 'OPEN' ? '🟢 Connected' : '🔴 Disconnected'}
      </div>

      <div className="task-list">
        {tasks.map(task => (
          <div key={task.id} className={task.completed ? 'completed' : ''}>
            <h3>{task.title}</h3>
            <p>{task.description}</p>
            <span className={`priority ${task.priority}`}>{task.priority}</span>
          </div>
        ))}
      </div>
    </div>
  );
}


// ===========================
// 3. Notification Helper
// ===========================

function showNotification(title, body) {
  // Browser notification
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(title, { body });
  }

  // Or use a toast library like react-hot-toast
  // toast.success(`${title}: ${body}`);
}


// ===========================
// 4. Next.js App Integration
// ===========================

// In your app/layout.tsx or pages/_app.tsx
export function AppWithWebSocket({ children }) {
  useEffect(() => {
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  return <>{children}</>;
}


// ===========================
// 5. TypeScript Types (Optional)
// ===========================

interface TaskCreatedMessage {
  type: 'task_created';
  data: {
    id: number;
    title: string;
    description: string;
    priority: 'low' | 'medium' | 'high';
    user_id: number;
    completed: boolean;
  };
}

interface TaskCompletedMessage {
  type: 'task_completed';
  data: {
    id: number;
    title: string;
    completed: boolean;
    completed_at: string;
  };
}

type WebSocketMessage =
  | TaskCreatedMessage
  | TaskCompletedMessage
  | { type: 'connected'; message: string }
  | { type: 'pong' };


// ===========================
// 6. Connection Status Component
// ===========================

export function WebSocketStatus({ readyState }) {
  const statusMap = {
    'CONNECTING': { text: 'Connecting...', color: 'yellow' },
    'OPEN': { text: 'Connected', color: 'green' },
    'CLOSING': { text: 'Disconnecting...', color: 'orange' },
    'CLOSED': { text: 'Disconnected', color: 'red' },
    'ERROR': { text: 'Error', color: 'red' }
  };

  const status = statusMap[readyState] || statusMap['CLOSED'];

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '8px',
      background: '#f5f5f5',
      borderRadius: '4px'
    }}>
      <div style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        background: status.color
      }} />
      <span>{status.text}</span>
    </div>
  );
}


// ===========================
// 7. Example Usage in Page
// ===========================

/*
import { useWebSocket } from '@/hooks/useWebSocket';
import { WebSocketStatus } from '@/components/WebSocketStatus';

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const token = localStorage.getItem('token');

  const { lastMessage, readyState } = useWebSocket(
    'ws://localhost:8000/ws/tasks',
    token
  );

  useEffect(() => {
    if (lastMessage?.type === 'task_created') {
      setTasks(prev => [lastMessage.data, ...prev]);
    }
  }, [lastMessage]);

  return (
    <div>
      <WebSocketStatus readyState={readyState} />
      <TaskList tasks={tasks} />
    </div>
  );
}
*/
