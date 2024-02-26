import React, { useState, useRef, KeyboardEvent } from 'react';
import './App.css';
import MessageBubble from './components/MessageBubble';
import { v4 as uuidv4 } from 'uuid';
import voiceIcon from './assets/voice.svg';
import sendIcon from './assets/send.svg';

interface IMessage {
  id: string;
  text: string;
  timestamp?: string;
  sender: 'user' | 'bot' | 'system';
  isLoading?: boolean;
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isInitialized, setIsInitialized] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSendMessage = async () => {
    const newTimestampFromUser = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const newMessageIdFromUser = uuidv4();

    const newMessageFromUser: IMessage = {
      id: newMessageIdFromUser,
      text: input,
      timestamp: newTimestampFromUser,
      sender: 'user',
    };

    setMessages(messages => [...messages, newMessageFromUser]);

    setInput('');

    const newTimestampFromBot = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const newMessageIdFromBot = uuidv4();
    if (isInitialized) {
      const newMessageFromBot: IMessage = {
        id: newMessageIdFromBot,
        text: input,
        timestamp: newTimestampFromBot,
        sender: 'bot',
        isLoading: true,
      };
      setMessages(messages => [...messages, newMessageFromBot]);
    }

    const requestBody = isInitialized ? { text: input } : { name: input };
    const requestUrl = isInitialized ? 'http://localhost:2024/send_text' : 'http://localhost:2024/init_chat';

    try {
      const response = await fetch(requestUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();

      if (!isInitialized) {
        setIsInitialized(true);
        setMessages(currentMessages => [...currentMessages, { id: uuidv4(), text: data.message, sender: 'system' }]);
      } else {
        setMessages(currentMessages =>
          currentMessages.map(message =>
            message.id === newMessageIdFromBot ? { ...message, text: data.response_text, timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), isLoading: false, sender: 'bot' } : message
          )
        );
        playResponseMp3(data.mp3_url);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(currentMessages =>
        currentMessages.map(message =>
          message.id === newMessageIdFromBot ? { ...message, text: 'Error sending message.', timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), isLoading: false } : message
        )
      );
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  // const playResponseMp3 = (url: string) => {
  //   const audio = new Audio(url);
  //   audio.play();
  // };

  const playResponseMp3 = (url: string) => {
    const audio = new Audio(url);
    const requestUrl = 'http://localhost:2024/audio_played';
    audio.onended = () => {
      const messageBody = JSON.stringify({ filename: url.split('/').pop() });
      console.log('Sending message:', messageBody);
      fetch(requestUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: messageBody,
      });
    };
    audio.play();
  };

  return (
    <div className="App">
      <div className="message-container">
        {messages.map(({ id, text, sender, timestamp, isLoading }) => (
          <MessageBubble key={id} text={text} timestamp={timestamp || ''} isUser={sender === 'user'} isLoading={isLoading} />
        ))}
      </div>
      <div className="input-container">
        <div className="input-wrapper">
          <input
            ref={inputRef}
            className="input-bar"
            type="text"
            placeholder={!isInitialized ? "Enter your name to start" : "Send your message..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
          />
          <button className="microphone-button">
            <img src={voiceIcon} alt="Microphone" />
          </button>
        </div>
        <button className="send-button" onClick={handleSendMessage} disabled={isLoading}>
          <img src={sendIcon} alt="Send" />
        </button>
      </div>
    </div>
  );
};

export default App;
