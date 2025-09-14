import React, { useState } from 'react';
const Sidebar: React.FC<{
  mode: 'chat' | 'agent' | 'settings';
  setMode: React.Dispatch<React.SetStateAction<'chat' | 'agent' | 'settings'>>;
}> = ({ mode, setMode }) => {
  return (
    <aside className="sidebar">
      <button onClick={() => setMode('chat')} aria-pressed={mode === 'chat'}>
        Chat
      </button>
      <button onClick={() => setMode('agent')} aria-pressed={mode === 'agent'}>
        Agent
      </button>
      <button onClick={() => setMode('settings')} aria-pressed={mode === 'settings'}>
        Settings
      </button>
    </aside>
  );
};
// import ChatMode from './components/ChatMode';
// import AgentMode from './components/AgentMode';
// import Settings from './components/Settings';
import './App.css';

function App() {
  const [mode, setMode] = useState<'chat' | 'agent' | 'settings'>('chat');
  return (
    <div className="app-container">
      <Sidebar mode={mode} setMode={setMode} />
      <main>
        {/* {mode === 'chat' && <ChatMode />} */}
        {/* {mode === 'agent' && <AgentMode />} */}
        {/* {mode === 'settings' && <Settings />} */}
      </main>
    </div>
  );
}
export default App;
