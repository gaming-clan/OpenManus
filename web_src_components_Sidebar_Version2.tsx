import React from 'react';

type SidebarMode = 'chat' | 'agent' | 'settings';

interface SidebarProps {
  mode: SidebarMode;
  setMode: (mode: SidebarMode) => void;
}

export default function Sidebar({ mode, setMode }: SidebarProps) {
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
