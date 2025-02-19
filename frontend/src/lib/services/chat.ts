import { chatMessages } from '$lib/stores/chat';

export class ChatService {
  private ws: WebSocket;

  constructor() {
    console.log('🚀 Initializing ChatService...');
    this.connect();
  }

  private connect() {
    console.log('🔌 Connecting to WebSocket...');
    this.ws = new WebSocket('ws://localhost:8000/ws/chat');
    
    this.ws.onopen = () => {
      console.log('✅ WebSocket connected successfully');
    };
    
    this.ws.onmessage = (event) => {
      console.log('📩 Received WebSocket message:', event.data);
      try {
        const parsed = JSON.parse(event.data);
        console.log('✨ Message parsé:', {
          type: parsed.type,
          text: parsed.text,
          icon: parsed.icon,
          table: parsed.table
        });
        chatMessages.handleWebSocketMessage(event.data);
      } catch (e) {
        console.error('❌ Erreur de parsing:', e);
        console.log('📄 Message brut reçu:', event.data);
        chatMessages.handleWebSocketMessage(event.data);
      }
    };

    this.ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      chatMessages.addMessage('Erreur de connexion au serveur', false, 'error', '⚠️');
    };

    this.ws.onclose = () => {
      console.log('🔌 WebSocket connection closed');
      chatMessages.addMessage('Connexion perdue', false, 'error', '⚠️');
    };
  }

  public sendMessage(message: string) {
    console.log('📤 Sending message:', message);
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(message);
      console.log('✅ Message sent successfully');
    } else {
      console.error('❌ WebSocket not connected (state:', this.ws.readyState, ')');
      chatMessages.addMessage('Impossible d\'envoyer le message : pas de connexion', false, 'error', '⚠️');
    }
  }

  public disconnect() {
    console.log('🔌 Disconnecting WebSocket...');
    this.ws.close();
  }
}
