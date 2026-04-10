#!/usr/bin/env python3
"""
Force deployment by making a small change
"""

import time

def create_deployment_trigger():
    """Create a small change to trigger deployment"""
    with open("d:/vpvsproject/backend/api/index.py", "r") as f:
        content = f.read()
    
    # Add a comment with timestamp to force deployment
    timestamp = int(time.time())
    new_content = content.replace(
        "app = FastAPI(title=\"VPVS API\")",
        f"app = FastAPI(title=\"VPVS API - Deployed {timestamp}\")"
    )
    
    with open("d:/vpvsproject/backend/api/index.py", "w") as f:
        f.write(new_content)
    
    print(f"Added deployment trigger: {timestamp}")

if __name__ == "__main__":
    create_deployment_trigger()
