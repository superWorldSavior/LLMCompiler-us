import { writable } from 'svelte/store';

export interface TableData {
  headers: string[];
  rows: any[][];
}

export interface ChatMessage {
  text: string;
  isUser: boolean;
  timestamp: Date;
  type?: 'thought' | 'response' | 'error';
  icon?: string;
  table?: TableData;
}

interface WebSocketMessage {
  type: 'thought' | 'response' | 'error';
  text: string;
  icon?: string;
  table?: TableData;
}

function createChatStore() {
  const { subscribe, update } = writable<ChatMessage[]>([]);

  return {
    subscribe,
    addMessage: (text: string, isUser: boolean, type?: 'thought' | 'response' | 'error', icon?: string, table?: TableData) => {
      const message: ChatMessage = {
        text,
        isUser,
        timestamp: new Date(),
        type,
        icon,
        table
      };
      update(messages => [...messages, message]);
    },
    handleWebSocketMessage: (data: string) => {
      try {
        console.log(' Store: Traitement du message WebSocket:', data);
        const message = JSON.parse(data) as WebSocketMessage;
        console.log(' Store: Message parsé:', message);
        update(messages => {
          console.log(' Store: Mise à jour des messages avec:', message);
          return [...messages, {
            text: message.text,
            isUser: false,
            timestamp: new Date(),
            type: message.type,
            icon: message.icon,
            table: message.table
          }];
        });
      } catch (e) {
        console.error(' Store: Erreur de traitement:', e);
        console.log(' Store: Message brut:', data);
        update(messages => [...messages, {
          text: data,
          isUser: false,
          timestamp: new Date(),
          type: 'response'
        }]);
      }
    },
    clear: () => {
      update(() => []);
    }
  };
}

export const chatMessages = createChatStore();
