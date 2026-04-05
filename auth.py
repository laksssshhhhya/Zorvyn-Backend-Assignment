from fastapi import Header, HTTPException

def require_admin(x_user_role: str = Header(default="Viewer")):
    if x_user_role != "Admin":
        raise HTTPException(status_code=403, detail="Admin required")
    return x_user_role

def require_analyst(x_user_role: str = Header(default="Viewer")):
    if x_user_role not in ["Admin", "Analyst"]:
        raise HTTPException(status_code=403, detail="Analyst required")
    return x_user_role

def require_viewer(x_user_role: str = Header(default="Viewer")):
    if x_user_role not in ["Admin", "Analyst", "Viewer"]:
        raise HTTPException(status_code=403, detail="Viewer required")
    return x_user_role
