import React from "react";
import './MessageBubble.css';

interface IMessageBubbleProps {
    text: string;
    timestamp: string;
    isUser: boolean;
    isLoading: boolean | undefined;
}

const MessageBubble: React.FC<IMessageBubbleProps> = ({ text, timestamp, isUser, isLoading }) => (
    <div className={`message ${isUser ? 'user' : 'bot'}`}>
      <div className={`bubble ${isUser ? 'user' : 'bot'}`}>
        {isLoading ? (
          <div className="typing-indicator"></div>
        ) : (
          <div>
            <div className="text">{text}</div>
            <div className="timestamp">{timestamp}</div>
          </div>
        )}
      </div>
    </div>
  );
  

export default MessageBubble