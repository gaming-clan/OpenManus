#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend_app_Version2 import create_app

if __name__ == "__main__":
    app = create_app()
    print("Starting OpenManus test server...")
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
