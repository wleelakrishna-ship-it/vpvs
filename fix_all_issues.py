#!/usr/bin/env python3
"""
Fix all remaining API issues at once
"""

import re

def fix_all_api_issues():
    """Fix all remaining API issues"""
    
    with open("d:/vpvsproject/backend/api/index.py", "r") as f:
        content = f.read()
    
    # Fix 1: Ensure proper order method syntax
    content = re.sub(
        r'\.order\("created_at", \{"ascending": False\}\)',
        '.order("created_at", desc=True)',
        content
    )
    
    # Fix 2: Ensure health endpoints are properly defined
    if '@app.get("/api/health")' not in content:
        # Add health endpoint before posts
        posts_start = content.find('@app.get("/api/posts")')
        if posts_start != -1:
            health_code = '''
@app.get("/api/health")
def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VPVS Backend API",
        "version": "2.0.0"
    }


@app.get("/health")
def root_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VPVS Backend API",
        "version": "2.0.0"
    }


'''
            content = content[:posts_start] + health_code + content[posts_start:]
    
    # Fix 3: Remove authentication from expense groups
    expense_groups_pattern = r'@app\.get\("/api/expense-groups"\)\s+def get_expense_groups\(authorization: Optional\[str\] = Header\(default=None\)\):'
    if re.search(expense_groups_pattern, content):
        content = re.sub(
            expense_groups_pattern,
            '@app.get("/api/expense-groups")\ndef get_expense_groups():',
            content
        )
        
        # Remove authentication check from expense groups
        auth_check_pattern = r'current_user = get_current_user\(authorization\)\s+if not current_user:\s+return _safe_error\("Authentication required", 401\)\s+'
        content = re.sub(auth_check_pattern, '', content)
        
        # Remove user filter from expense groups query
        user_filter_pattern = r'\.eq\("created_by", current_user\["id"\]\)'
        content = re.sub(user_filter_pattern, '', content)
    
    # Fix 4: Ensure proper response format for all endpoints
    # Fix expenses endpoint to return proper format
    if 'return [{"error":"Authentication required"},401]' in content:
        content = content.replace(
            'return [{"error":"Authentication required"},401]',
            'return _safe_error("Authentication required", 401)'
        )
    
    # Fix 5: Add proper error handling for UUID validation
    uuid_pattern = r'@app\.get\("/api/posts/\{post_id\}/likes"\)\s+def get_post_likes\(post_id: str\):'
    if re.search(uuid_pattern, content):
        likes_function = '''@app.get("/api/posts/{post_id}/likes")
def get_post_likes(post_id: str):
    try:
        # Validate UUID format
        from uuid import UUID
        try:
            UUID(post_id)  # Will raise ValueError if invalid
        except ValueError:
            return _safe_error("Invalid post ID format", 400)
        
        sb = get_admin_client()
        res = (
            sb.table("likes")
            .select("id,post_id,username,created_at")
            .eq("post_id", post_id)
            .order("created_at", desc=True)
            .execute()
        )
        return {"likes": res.data or []}
    except Exception as exc:
        return _safe_error(str(exc))'''
        
        # Replace the entire likes function
        likes_start = content.find('@app.get("/api/posts/{post_id}/likes")')
        next_function_start = content.find('\n\n@app.get(', likes_start + 1)
        if next_function_start == -1:
            next_function_start = len(content)
        
        content = content[:likes_start] + likes_function + content[next_function_start:]
    
    # Write the fixed content
    with open("d:/vpvsproject/backend/api/index.py", "w") as f:
        f.write(content)
    
    print("All API issues fixed!")

if __name__ == "__main__":
    fix_all_api_issues()
