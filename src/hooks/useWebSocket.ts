import { useEffect, useRef, useState, useCallback } from 'react';
import { WebSocketMessage } from '../types';

export function useWebSocket(clientId: string, onMessageReceived?: (msg: WebSocketMessage) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.close();
    }

    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // Using relative endpoint behind express gateway path mapping
    const wsUrl = `${wsProto}//${window.location.host}/ws/progress?clientId=${clientId}`;
    
    console.log(`[ReelVault WS] Registering transit link to: ${wsUrl}`);
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log(`[ReelVault WS] Active pipeline synchronized. Client ID: ${clientId}`);
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (onMessageReceived) {
          onMessageReceived(msg);
        }
      } catch (e) {
        // Fallback for raw text pings
        if (event.data !== 'pong') {
          console.log('[ReelVault WS] Received message:', event.data);
        }
      }
    };

    ws.onclose = () => {
      console.log('[ReelVault WS] Pipeline closed.');
      setIsConnected(false);
    };

    ws.onerror = (err) => {
      console.error('[ReelVault WS] Link error:', err);
      setIsConnected(false);
    };
  }, [clientId, onMessageReceived]);

  useEffect(() => {
    connect();
    
    // Heartbeat ping timer to prevent background timeout
    const interval = setInterval(() => {
      if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.send('ping');
      }
    }, 15000);

    return () => {
      clearInterval(interval);
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [connect]);

  return { isConnected, reconnect: connect };
}
