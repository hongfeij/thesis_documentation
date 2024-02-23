import React, { useState, useRef, KeyboardEvent } from 'react';
import { ClipLoader } from 'react-spinners';
import './App.scss';
import MessageBubble from "../components/MessageBubble";

interface IMessage {
  id: number;
  text: string;
  timestamp?: string;
  sender: 'user' | 'bot' | 'system';
}

const App: React.FC = () => {
  const [messages, setMessages] = useState<IMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isInitialized, setIsInitialized] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleKeyPress = async (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && input.trim()) {
      setIsLoading(true);
      const newTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const requestBody = isInitialized ? { text: input } : { name: input };
      const requestUrl = isInitialized ? 'http://localhost:5000/send_text' : 'http://localhost:5000/init_chat';

      try {
        const response = await fetch(requestUrl, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok) {
          throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (!isInitialized) {
          setMessages([...messages, { id: Date.now(), text: data.message, sender: 'system' }]);
          setIsInitialized(true);
        } else {
          const newMessage: IMessage = { id: Date.now(), text: input, timestamp: newTimestamp, sender: 'user' };
          const botResponse: IMessage = { id: Date.now(), text: data.response_text, timestamp: newTimestamp, sender: 'bot' };
          setMessages([...messages, newMessage, botResponse]);
          playResponseMp3(data.mp3_url);
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setInput('');
        setIsLoading(false);
      }
    }
  };

  const playResponseMp3 = (url: string) => {
    const audio = new Audio(url);
    audio.play();
  };

  return (
    <div className="App">
      <div className="message-container">
        {messages.map(({ id, text, sender, timestamp }) => (
          <MessageBubble key={id} text={text} timestamp={timestamp || ''} isUser={sender === 'user'} />
        ))}
        {isLoading && <ClipLoader color="#000000" loading={true} size={50} />}
      </div>
      <div className="input-container">
        <input
          ref={inputRef}
          className="input-bar"
          type="text"
          placeholder={!isInitialized ? "Enter your name..." : "Type your message..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
        />
      </div>
    </div>
  );
};

export default App;
