"""
Helper utility functions for NDC UK Backend
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import secrets
import string
from app.utils.constants import MEMBERSHIP_NUMBER_FORMAT

def generate_membership_number(year: int, sequence: int) -> str:
    """Generate membership number in NDC format"""
    return MEMBERSHIP_NUMBER_FORMAT.format(year=year, number=sequence)

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_reset_token() -> str:
    """Generate password reset token"""
    return generate_secure_token(64)

def calculate_age(date_of_birth: datetime) -> int:
    """Calculate age from date of birth"""
    today = datetime.now().date()
    dob = date_of_birth.date() if isinstance(date_of_birth, datetime) else date_of_birth
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def format_phone_number(phone: str) -> str:
    """Format UK phone number consistently"""
    # Remove all non-digit characters except +
    cleaned = ''.join(char for char in phone if char.isdigit() or char == '+')
    
    # Convert to standard format
    if cleaned.startswith('44'):
        cleaned = '+' + cleaned
    elif cleaned.startswith('0'):
        cleaned = '+44' + cleaned[1:]
    elif not cleaned.startswith('+44'):
        cleaned = '+44' + cleaned
    
    return cleaned

def extract_permissions(roles_data: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Extract and merge permissions from multiple roles"""
    all_permissions = {}
    
    for role in roles_data:
        if not role.get('is_active', True):
            continue
            
        permissions = role.get('permissions', {})
        
        for resource, actions in permissions.items():
            if resource not in all_permissions:
                all_permissions[resource] = []
            
            if isinstance(actions, list):
                all_permissions[resource].extend(actions)
            elif actions is True or actions == "all":
                all_permissions[resource] = ["all"]
            elif isinstance(actions, str):
                all_permissions[resource].append(actions)
    
    # Remove duplicates and sort
    for resource in all_permissions:
        if "all" in all_permissions[resource]:
            all_permissions[resource] = ["all"]
        else:
            all_permissions[resource] = sorted(list(set(all_permissions[resource])))
    
    return all_permissions

def has_permission(user_permissions: Dict[str, List[str]], resource: str, action: str) -> bool:
    """Check if user has specific permission"""
    if not user_permissions:
        return False
    
    resource_permissions = user_permissions.get(resource, [])
    return "all" in resource_permissions or action in resource_permissions

def is_leadership_role(role_name: str) -> bool:
    """Check if role is a leadership role"""
    leadership_roles = [
        "Chairman", "Vice Chairman", "Secretary", "Assistant Secretary",
        "Branch Chairman", "Branch Secretary"
    ]
    return role_name in leadership_roles

def is_chapter_role(role_name: str) -> bool:
    """Check if role is a chapter-level role"""
    chapter_roles = [
        "Chairman", "Vice Chairman", "Secretary", "Assistant Secretary",
        "Treasurer", "Assistant Treasurer", "Organiser", "Deputy Organiser",
        "Youth Organiser", "Deputy Youth Organiser", "Women's Organiser",
        "Deputy Women's Organiser", "Public Relations Officer (PRO)", 
        "Deputy PRO", "Welfare Officer"
    ]
    return role_name in chapter_roles

def is_branch_role(role_name: str) -> bool:
    """Check if role is a branch-level role"""
    return role_name.startswith("Branch ")

def is_committee_role(role_name: str) -> bool:
    """Check if role is a committee role"""
    return "Committee" in role_name

def paginate_results(data: List[Any], page: int, size: int) -> Dict[str, Any]:
    """Paginate a list of results"""
    total = len(data)
    start = (page - 1) * size
    end = start + size
    
    return {
        "items": data[start:end],
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size
    }

def build_user_context(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build user context with roles and permissions"""
    roles = []
    permissions = {}
    
    # Extract roles from executive assignments
    for assignment in user_data.get('executive_assignments', []):
        if assignment.get('is_active'):
            role_data = assignment.get('roles', {})
            roles.append({
                'id': role_data.get('id'),
                'name': role_data.get('name'),
                'scope_type': role_data.get('scope_type'),
                'chapter_id': assignment.get('chapter_id'),
                'branch_id': assignment.get('branch_id')
            })
            
            # Merge permissions
            role_permissions = role_data.get('permissions', {})
            for resource, actions in role_permissions.items():
                if resource not in permissions:
                    permissions[resource] = []
                
                if isinstance(actions, list):
                    permissions[resource].extend(actions)
                elif actions is True:
                    permissions[resource] = ["all"]
    
    # Remove duplicate permissions
    for resource in permissions:
        if "all" in permissions[resource]:
            permissions[resource] = ["all"]
        else:
            permissions[resource] = list(set(permissions[resource]))
    
    return {
        'user_id': user_data.get('id'),
        'full_name': user_data.get('full_name'),
        'email': user_data.get('email'),
        'status': user_data.get('status'),
        'roles': roles,
        'permissions': permissions,
        'is_leadership': any(is_leadership_role(role['name']) for role in roles),
        'is_chapter_executive': any(is_chapter_role(role['name']) for role in roles),
        'is_branch_executive': any(is_branch_role(role['name']) for role in roles)
    }

def format_error_response(message: str, errors: Optional[List[str]] = None) -> Dict[str, Any]:
    """Format standardized error response"""
    response = {"message": message}
    if errors:
        response["errors"] = errors
    return response

def format_success_response(message: str, data: Optional[Any] = None) -> Dict[str, Any]:
    """Format standardized success response"""
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return response

def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary"""
    return {k: v for k, v in data.items() if v is not None}

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result

def truncate_string(text: str, max_length: int = 100) -> str:
    """Truncate string to maximum length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    import re
    
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().replace(' ', '-')
    
    # Remove non-alphanumeric characters except hyphens
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    
    # Remove leading/trailing hyphens
    return slug.strip('-')

def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is valid UUID"""
    import re
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, uuid_string, re.IGNORECASE))

def get_user_display_name(user_data: Dict[str, Any]) -> str:
    """Get user's display name"""
    full_name = user_data.get('full_name', '')
    if full_name:
        return full_name
    
    email = user_data.get('email', '')
    if email:
        return email.split('@')[0]
    
    return f"User {user_data.get('id', 'Unknown')[:8]}"