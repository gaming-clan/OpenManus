import React, { useState } from 'react';

export default function ChatMode() {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<{ user: string, agent: string }[]>([]);

  async function send() {
    if (!input.trim()) return;
    const userMessage = input;
    setInput('');
    setHistory(h => [...h, { user: userMessage, agent: "..." }]);
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input: userMessage })
    });
    const data = await res.json();
    setHistory(h => h.slice(0, -1).concat([{ user: userMessage, agent: data.output }]));
  }

  return (
    <div className="chat-mode">
      <div className="chat-history">
        {history.map((msg, i) => (
          <div key={i} className="chat-entry">
            <div className="user">{msg.user}</div>
            <div className="agent">{msg.agent}</div>
          </div>
        ))}
      </div>
      <div className="chat-input">
        <textarea value={input} onChange={e => setInput(e.target.value)} />
        <button onClick={send}>Send</button>
      </div>
    </div>
  );
}