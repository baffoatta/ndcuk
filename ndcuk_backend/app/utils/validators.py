"""
Custom validators for NDC UK Backend
"""
from typing import Optional
import re
from datetime import datetime, date
from app.core.exceptions import ValidationException

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """Validate UK phone number format"""
    # UK phone number patterns (mobile and landline)
    patterns = [
        r'^(\+44|0)[1-9]\d{8,9}$',  # General UK format
        r'^(\+44|0)7\d{9}$',        # Mobile format
        r'^(\+44|0)[1-9]\d{8}$'     # Landline format
    ]
    
    return any(re.match(pattern, phone.replace(' ', '').replace('-', '')) for pattern in patterns)

def validate_membership_number(membership_number: str) -> bool:
    """Validate membership number format (NDC-YYYY-XXXX)"""
    pattern = r'^NDC-\d{4}-\d{4}$'
    return re.match(pattern, membership_number) is not None

def validate_password_strength(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase, lowercase, digit, and special character
    patterns = [
        r'[A-Z]',  # Uppercase
        r'[a-z]',  # Lowercase  
        r'\d',     # Digit
        r'[!@#$%^&*(),.?":{}|<>]'  # Special character
    ]
    
    return all(re.search(pattern, password) for pattern in patterns)

def validate_date_of_birth(dob: date) -> bool:
    """Validate date of birth (must be at least 16 years old)"""
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return 16 <= age <= 120

def validate_branch_name(name: str) -> bool:
    """Validate branch name format"""
    if not name or len(name.strip()) < 2:
        return False
    
    # Allow letters, numbers, spaces, hyphens, and apostrophes
    pattern = r"^[a-zA-Z0-9\s\-']+$"
    return re.match(pattern, name.strip()) is not None

def validate_role_name(name: str) -> bool:
    """Validate role name format"""
    if not name or len(name.strip()) < 2:
        return False
    
    # Allow letters, spaces, parentheses, and common punctuation
    pattern = r"^[a-zA-Z\s\(\)\-'&]+$"
    return re.match(pattern, name.strip()) is not None

def validate_uuid(uuid_string: str) -> bool:
    """Validate UUID format"""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$'
    return re.match(uuid_pattern, uuid_string, re.IGNORECASE) is not None

def validate_file_type(filename: str, allowed_types: list) -> bool:
    """Validate file extension"""
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return extension in [t.lower() for t in allowed_types]

def validate_image_file(filename: str) -> bool:
    """Validate image file extension"""
    allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    return validate_file_type(filename, allowed_extensions)

def sanitize_string(input_string: str) -> str:
    """Sanitize string input by removing harmful characters"""
    if not input_string:
        return ""
    
    # Remove control characters and normalize whitespace
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_string)
    sanitized = ' '.join(sanitized.split())
    
    return sanitized.strip()

def validate_name(name: str) -> bool:
    """Validate person name (allows letters, spaces, hyphens, apostrophes)"""
    if not name or len(name.strip()) < 2:
        return False
    
    pattern = r"^[a-zA-Z\s\-'\.]+$"
    return re.match(pattern, name.strip()) is not None

def validate_address(address: str) -> bool:
    """Validate address format"""
    if not address or len(address.strip()) < 5:
        return False
    
    # Allow letters, numbers, spaces, and common address punctuation
    pattern = r"^[a-zA-Z0-9\s\-',\.\/]+$"
    return re.match(pattern, address.strip()) is not None

class PasswordValidator:
    """Password validation class with detailed feedback"""
    
    @staticmethod
    def validate(password: str) -> tuple[bool, list[str]]:
        """Validate password and return detailed feedback"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        if len(password) > 128:
            errors.append("Password must be less than 128 characters")
        
        return len(errors) == 0, errors

def validate_registration_data(
    email: str,
    password: str,
    full_name: str,
    phone: Optional[str] = None,
    date_of_birth: Optional[date] = None
) -> tuple[bool, list[str]]:
    """Validate user registration data"""
    errors = []
    
    # Validate email
    if not validate_email(email):
        errors.append("Invalid email format")
    
    # Validate password
    password_valid, password_errors = PasswordValidator.validate(password)
    if not password_valid:
        errors.extend(password_errors)
    
    # Validate name
    if not validate_name(full_name):
        errors.append("Invalid name format")
    
    # Validate phone (if provided)
    if phone and not validate_phone(phone):
        errors.append("Invalid phone number format")
    
    # Validate date of birth (if provided)
    if date_of_birth and not validate_date_of_birth(date_of_birth):
        errors.append("Invalid date of birth (must be 16-120 years old)")
    
    return len(errors) == 0, errors