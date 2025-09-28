# OpenManus Installation and Usage Guide

This guide provides detailed instructions for installing and using the OpenManus web interface with the new HTML/CSS/JavaScript frontend.

## Quick Start (Web Interface)

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/gaming-clan/OpenManus.git
cd OpenManus
```

2. Install minimal dependencies for web interface:
```bash
pip install -r requirements.min.txt
```

### Running the Web Interface

Start the Flask development server:
```bash
python3 test_server.py
```

The web interface will be available at `http://localhost:5000`

## Web Interface Features

### Agent Mode
- **View Logs**: Monitor real-time agent activity and system status
- **Start Agent**: Initialize the default agent or select a specific agent type
- **Stop Agent**: Safely terminate the running agent
- **Refresh Logs**: Manually update the log display

### Chat Mode
- **Send Messages**: Type messages and receive responses from the AI agent
- **Chat History**: View conversation history with proper formatting
- **Clear Chat**: Reset the conversation history

## API Endpoints

The backend provides the following REST API endpoints:

- `GET /api/health` - Health check endpoint
- `GET /api/agent/logs` - Retrieve agent logs
- `POST /api/agent/start` - Start an agent
- `POST /api/agent/stop` - Stop the running agent
- `POST /api/chat` - Send a chat message and receive a response

## Project Structure (Web Interface)

```
OpenManus/
├── web/                              # Frontend files
│   ├── index.html                   # Main HTML file
│   └── static/
│       ├── styles.css               # CSS styling
│       └── app.js                   # JavaScript functionality
├── backend_app_Version2.py          # Flask application
├── backend_routes_Version2.py       # API routes
├── backend_agent_controller.py      # Agent control logic
├── test_server.py                   # Development server
└── requirements.min.txt             # Minimal dependencies
```

## Development

### Frontend Development
The frontend uses vanilla HTML, CSS, and JavaScript for maximum compatibility and minimal dependencies. Key features include:

- Responsive design that works on desktop and mobile
- Modern CSS with gradients, animations, and hover effects
- Asynchronous JavaScript for smooth API interactions
- Real-time log updates and chat functionality

### Backend Development
The backend is built with Flask and provides:

- RESTful API design
- Agent state management
- Logging and error handling
- Static file serving for the frontend

## Troubleshooting

### Common Issues

1. **Port 5000 already in use**
   - Kill the process using the port: `fuser -k 5000/tcp`
   - Or modify `test_server.py` to use a different port

2. **Permission denied errors**
   - Use `sudo pip install` if needed
   - Check file permissions in the project directory

3. **Module not found errors**
   - Ensure you're in the correct directory
   - Verify all dependencies are installed

### Testing the Installation

1. Start the server: `python3 test_server.py`
2. Open browser to `http://localhost:5000`
3. Test Agent Mode: Click "Refresh Logs", "Start Agent", "Stop Agent"
4. Test Chat Mode: Switch to Chat Mode, send a test message
5. Verify API endpoints work: `curl http://localhost:5000/api/health`

## Full Installation (Original OpenManus)

For the complete OpenManus experience with all features, follow the original installation instructions in the main README.md file.

## Contributing

When contributing to the web interface:

1. Frontend changes: Modify files in `web/` directory
2. Backend changes: Update `backend_*.py` files
3. Test thoroughly with both Agent Mode and Chat Mode
4. Ensure responsive design works on different screen sizes
