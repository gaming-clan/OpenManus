import React, { useEffect, useState } from 'react';

export default function Settings() {
  const [keys, setKeys] = useState({});
  const [edit, setEdit] = useState(false);

  useEffect(() => {
    fetch('/api/keys').then(r => r.json()).then(setKeys);
  }, []);

  function save() {
    fetch('/api/keys', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(keys)
    }).then(() => setEdit(false));
  }

  return (
    <div className="settings">
      <h3>API Keys</h3>
      {!edit ? (
        <div>
          <ul>
            {Object.entries(keys).map(([k, v]) => (
              <li key={k}>{k}: {v ? '********' : <em>Not set</em>}</li>
            ))}
          </ul>
          <button onClick={() => setEdit(true)}>Edit Keys</button>
        </div>
      ) : (
        <div>
          {Object.entries(keys).map(([k, v]) => (
            <div key={k}>
              <label>{k}</label>
              <input value={v} type="text" onChange={e => setKeys({ ...keys, [k]: e.target.value })} />
            </div>
          ))}
          <button onClick={save}>Save</button>
        </div>
      )}
    </div>
  );
}