import React, { useEffect, useState } from 'react';

export default function AgentMode() {
  const [logs, setLogs] = useState<string[]>([]);

  useEffect(() => {
    fetch('/api/agent/logs')
      .then(r => r.json())
      .then(data => setLogs(data.logs || []));
  }, []);

  return (
    <div className="agent-mode">
      <h3>Agent Logs</h3>
      <pre className="agent-logs">
        {logs.join('\n')}
      </pre>
      {/* Add agent controls/selection here */}
    </div>
  );
}