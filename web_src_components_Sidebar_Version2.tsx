import React from 'react';

export default function Sidebar({ mode, setMode }) {
  return (
    <nav className="sidebar">
      <h2>OpenManus</h2>
      <ul>
        <li className={mode === 'chat' ? 'active' : ''} onClick={() => setMode('chat')}>Chat Mode</li>
        <li className={mode === 'agent' ? 'active' : ''} onClick={() => setMode('agent')}>Agent Mode</li>
        <li className={mode === 'settings' ? 'active' : ''} onClick={() => setMode('settings')}>Settings</li>
      </ul>
    </nav>
  );
}