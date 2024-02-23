import React from "react";
import './MessageBubble.scss';

interface IMessageBubbleProps {
    text: string;
    timestamp: string;
    isUser: boolean;
}

const MessageBubble: React.FC<IMessageBubbleProps> = ({ text, timestamp, isUser }) => (
    <div className={`message ${isUser ? 'user' : 'bot'}`}>
        <div className={`bubble ${isUser ? 'user' : 'bot'}`}>
            <div className="text">{text}</div>
            <div className="timestamp">{timestamp}</div>
        </div>
    </div>
);

export default MessageBubble