#!/usr/bin/env python3
"""
Remove all authentication-related code from the backend API
"""

import re

def remove_all_authentication():
    """Remove all authentication requirements from the backend"""
    
    with open("d:/vpvsproject/backend/api/index.py", "r") as f:
        content = f.read()
    
    # Remove authentication functions
    auth_functions = [
        'def _extract_token\(authorization: Optional\[str\]\) -> str:.*?return parts\[1\]',
        'def require_admin\(authorization: Optional\[str\]\) -> Dict\[str, Any\]:.*?return user',
        'def get_current_user\(authorization: Optional\[str\]\) -> Dict\[str, Any\]:.*?return None'
    ]
    
    for func_pattern in auth_functions:
        content = re.sub(func_pattern, '', content, flags=re.DOTALL)
    
    # Remove Header imports and parameters
    content = re.sub(r', authorization: Optional\[str\] = Header\(default=None\)', '', content)
    content = re.sub(r'authorization: Optional\[str\] = Header\(default=None\)', '', content)
    
    # Remove authentication checks
    auth_checks = [
        r'current_user = get_current_user\(authorization\)\s+if not current_user:\s+return _safe_error\("Authentication required", 401\)\s+',
        r'current_user = get_current_user\(authorization\)\s+if not current_user:\s+return _safe_error\("Authentication required", 401\)',
        r'if not current_user:\s+return _safe_error\("Authentication required", 401\)\s+',
        r'if not current_user:\s+return _safe_error\("Authentication required", 401\)'
    ]
    
    for check_pattern in auth_checks:
        content = re.sub(check_pattern, '', content)
    
    # Remove admin checks
    admin_checks = [
        r'is_admin = current_user\.get\("is_admin", False\)\s+if not is_admin:\s+return _safe_error\("Admin access required", 403\)\s+',
        r'is_admin = current_user\.get\("is_admin", False\)\s+if not is_admin:\s+return _safe_error\("Admin access required", 403\)',
        r'if not is_admin:\s+return _safe_error\("Admin access required", 403\)\s+',
        r'if not is_admin:\s+return _safe_error\("Admin access required", 403\)'
    ]
    
    for admin_pattern in admin_checks:
        content = re.sub(admin_pattern, '', content)
    
    # Remove user ownership checks
    ownership_checks = [
        r'is_owner = current_user\.get\("id"\) == post\.get\("created_by"\)\s+if not \(is_admin or is_owner\):\s+return _safe_error\("Permission denied", 403\)\s+',
        r'is_owner = current_user\.get\("id"\) == post\.get\("created_by"\)\s+if not \(is_admin or is_owner\):\s+return _safe_error\("Permission denied", 403\)',
        r'if not \(is_admin or is_owner\):\s+return _safe_error\("Permission denied", 403\)\s+',
        r'if not \(is_admin or is_owner\):\s+return _safe_error\("Permission denied", 403\)'
    ]
    
    for ownership_pattern in ownership_checks:
        content = re.sub(ownership_pattern, '', content)
    
    # Remove user filters from queries
    user_filters = [
        r'\.eq\("created_by", current_user\["id"\]\)',
        r'\.eq\("user_id", current_user\["id"\]\)',
        r'current_user\["id"\]'
    ]
    
    for filter_pattern in user_filters:
        content = re.sub(filter_pattern, '', content)
    
    # Fix login endpoint to not require authentication
    login_pattern = r'@app\.post\("/api/auth/login"\)\s+def login\(payload: Dict\[str, Any\]\):.*?return \{"user": user, "token": token\}'
    simple_login = '''@app.post("/api/auth/login")
def login(payload: Dict[str, Any]):
    try:
        username = payload.get("username")
        password = payload.get("password")
        
        if not username or not password:
            return _safe_error("Username and password required", 400)
        
        sb = get_admin_client()
        res = (
            sb.table("profiles")
            .select("*")
            .eq("username", username)
            .execute()
        )
        
        if not res.data:
            return _safe_error("User not found", 404)
        
        user = res.data[0]
        return {"user": user, "token": "mock-token"}
    except Exception as exc:
        return _safe_error(str(exc))'''
    
    content = re.sub(login_pattern, simple_login, content, flags=re.DOTALL)
    
    # Remove empty lines that might be left
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    # Write the modified content
    with open("d:/vpvsproject/backend/api/index.py", "w") as f:
        f.write(content)
    
    print("All authentication code removed successfully!")

if __name__ == "__main__":
    remove_all_authentication()
