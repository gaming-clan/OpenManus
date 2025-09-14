import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatMode from './components/ChatMode';
import AgentMode from './components/AgentMode';
import Settings from './components/Settings';
import './App.css';

function App() {
  const [mode, setMode] = useState<'chat' | 'agent' | 'settings'>('chat');
  return (
    <div className="app-container">
      <Sidebar mode={mode} setMode={setMode} />
      <main>
        {mode === 'chat' && <ChatMode />}
        {mode === 'agent' && <AgentMode />}
        {mode === 'settings' && <Settings />}
      </main>
    </div>
  );
}
export default App;