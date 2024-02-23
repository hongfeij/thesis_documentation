import React, { useState, useRef } from 'react';
import axios from 'axios';
import { ClipLoader } from 'react-spinners';
import './App.css';

const MessageBubble = ({ text, timestamp, isUser }) => (
  <div className={`message ${isUser ? 'user' : 'bot'}`}>
    <div className={`bubble ${isUser ? 'user' : 'bot'}`}>
      <div className="text">{text}</div>
      <div className="timestamp">{timestamp}</div>
    </div>
  </div>
);

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const inputRef = useRef(null);

  const handleKeyPress = async (e) => {
    if (e.key === 'Enter' && input.trim()) {
      setIsLoading(true);
      const newTimestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      if (!isInitialized) {
        try {
          const response = await axios.post('http://localhost:5000/init_chat', { name: input });
          setMessages([...messages, { id: Date.now(), text: response.data.message, sender: 'system' }]);
          setIsInitialized(true);
        } catch (error) {
          console.error('Error initializing chat:', error);
        }
      } else {
        const newMessage = { id: Date.now(), text: input, timestamp: newTimestamp, sender: 'user' };
        setMessages([...messages, newMessage]);

        try {
          const response = await axios.post('http://localhost:5000/send_text', { text: input });
          const botResponse = { id: Date.now(), text: response.data.response_text, timestamp: newTimestamp, sender: 'bot' };
          setMessages([...messages, newMessage, botResponse]);
          playResponseMp3(response.data.mp3_url);
        } catch (error) {
          console.error('Error sending message:', error);
        }
      }
      setInput('');
      setIsLoading(false);
    }
  };

  const playResponseMp3 = (url) => {
    const audio = new Audio(url);
    audio.play();
  };

  return (
    <div className="App">
      <div className="message-container">
        {messages.map(({ id, text, sender, timestamp }) => (
          <MessageBubble key={id} text={text} timestamp={timestamp} isUser={sender === 'user'} />
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
          onKeyPress={(e) => e.key === 'Enter' && handleKeyPress(e)}
          disabled={isLoading}
        />
      </div>
    </div>
  );
}

export default App;
