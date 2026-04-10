#!/usr/bin/env python3
"""
Force a new deployment by making a timestamp change
"""

import time

def force_deployment():
    """Force deployment by updating timestamp"""
    with open("d:/vpvsproject/backend/api/index.py", "r") as f:
        content = f.read()
    
    # Update the version with timestamp
    timestamp = int(time.time())
    new_content = content.replace(
        '"version": "2.0.0"',
        f'"version": "2.0.0-{timestamp}"'
    )
    
    with open("d:/vpvsproject/backend/api/index.py", "w") as f:
        f.write(new_content)
    
    print(f"Forced deployment with timestamp: {timestamp}")

if __name__ == "__main__":
    force_deployment()
