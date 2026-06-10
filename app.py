#!/usr/bin/env python3
# Entry point to run the Flask application from the root directory
from backend.app import app

if __name__ == "__main__":
    app.run(debug=False, port=5001)