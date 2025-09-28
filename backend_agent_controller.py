import asyncio
import json
import time
from datetime import datetime

# Global state for agent management
agent_state = {
    "running": False,
    "logs": [],
    "last_activity": None
}

def handle_chat(data):
    """Handle chat requests from the frontend"""
    try:
        user_input = data.get("input", "")
        if not user_input:
            return {"output": "Please provide a message.", "error": True}
        
        # Simulate processing time
        time.sleep(1)
        
        # Simple echo response for testing
        response = f"Echo: {user_input}"
        
        # Add to logs
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        agent_state["logs"].append(f"[{timestamp}] Chat: User said '{user_input}', Agent responded '{response}'")
        agent_state["last_activity"] = timestamp
        
        return {"output": response, "error": False}
        
    except Exception as e:
        error_msg = f"Error processing chat: {str(e)}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        agent_state["logs"].append(f"[{timestamp}] ERROR: {error_msg}")
        return {"output": error_msg, "error": True}


def handle_agent(data):
    """Handle agent control requests (start/stop)"""
    try:
        action = data.get("action", "")
        agent_type = data.get("agent_type", "default")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if action == "start":
            if agent_state["running"]:
                return {"status": "error", "message": "Agent is already running"}
            
            agent_state["running"] = True
            agent_state["last_activity"] = timestamp
            log_msg = f"[{timestamp}] Agent '{agent_type}' started successfully"
            agent_state["logs"].append(log_msg)
            
            return {"status": "success", "message": f"Agent '{agent_type}' started"}
            
        elif action == "stop":
            if not agent_state["running"]:
                return {"status": "error", "message": "Agent is not running"}
            
            agent_state["running"] = False
            agent_state["last_activity"] = timestamp
            log_msg = f"[{timestamp}] Agent stopped"
            agent_state["logs"].append(log_msg)
            
            return {"status": "success", "message": "Agent stopped"}
            
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}
            
    except Exception as e:
        error_msg = f"Error handling agent request: {str(e)}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        agent_state["logs"].append(f"[{timestamp}] ERROR: {error_msg}")
        return {"status": "error", "message": error_msg}


def get_logs():
    """Get agent logs for the frontend"""
    try:
        # Add system info to logs
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "RUNNING" if agent_state["running"] else "STOPPED"
        
        system_info = [
            f"=== OpenManus Agent System ===",
            f"Current Time: {timestamp}",
            f"Agent Status: {status}",
            f"Last Activity: {agent_state['last_activity'] or 'None'}",
            f"Total Log Entries: {len(agent_state['logs'])}",
            "=" * 30
        ]
        
        # Combine system info with actual logs
        all_logs = system_info + agent_state["logs"]
        
        # Keep only last 100 log entries to prevent memory issues
        if len(agent_state["logs"]) > 100:
            agent_state["logs"] = agent_state["logs"][-100:]
        
        return {"logs": all_logs, "status": "success"}
        
    except Exception as e:
        error_msg = f"Error retrieving logs: {str(e)}"
        return {"logs": [error_msg], "status": "error"}


# Initialize with some sample logs
def initialize_logs():
    """Initialize the system with some sample logs"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    agent_state["logs"] = [
        f"[{timestamp}] System initialized",
        f"[{timestamp}] Backend API ready",
        f"[{timestamp}] Waiting for commands..."
    ]
    agent_state["last_activity"] = timestamp

# Initialize on module load
initialize_logs()
