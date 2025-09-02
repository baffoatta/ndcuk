"""
Application constants for NDC UK Backend
"""

# User status constants
USER_STATUS = {
    "NOT_APPROVED": "not_approved",
    "PENDING_APPROVAL": "pending_approval", 
    "APPROVED": "approved",
    "SUSPENDED": "suspended",
    "EXPIRED": "expired"
}

# Membership status constants
MEMBERSHIP_STATUS = {
    "PENDING": "pending",
    "ACTIVE": "active",
    "LAPSED": "lapsed",
    "SUSPENDED": "suspended"
}

# Branch status constants
BRANCH_STATUS = {
    "ACTIVE": "active",
    "INACTIVE": "inactive",
    "PENDING": "pending"
}

# Role scope constants
ROLE_SCOPE = {
    "CHAPTER": "chapter",
    "BRANCH": "branch",
    "BOTH": "both"
}

# Chapter-level executive roles
CHAPTER_EXECUTIVES = [
    "Chairman",
    "Vice Chairman", 
    "Secretary",
    "Assistant Secretary",
    "Treasurer",
    "Assistant Treasurer",
    "Organiser",
    "Deputy Organiser",
    "Youth Organiser",
    "Deputy Youth Organiser",
    "Women's Organiser",
    "Deputy Women's Organiser",
    "Public Relations Officer (PRO)",
    "Deputy PRO",
    "Welfare Officer"
]

# Branch-level executive roles
BRANCH_EXECUTIVES = [
    "Branch Chairman",
    "Branch Secretary",
    "Branch Treasurer", 
    "Branch Organiser",
    "Branch Youth Organiser",
    "Branch Women's Organiser",
    "Branch Welfare Officer",
    "Branch PRO",
    "Branch Executive Member"
]

# Committee roles
COMMITTEE_ROLES = [
    "Finance Committee Chair",
    "Finance Committee Member",
    "Public Relations Committee Chair", 
    "Public Relations Committee Member",
    "Research Committee Chair",
    "Research Committee Member",
    "Organisation Committee Chair",
    "Organisation Committee Member",
    "Welfare Committee Chair",
    "Welfare Committee Member",
    "Complaints Committee Chair",
    "Complaints Committee Member",
    "Disciplinary Committee Chair",
    "Disciplinary Committee Member",
    "Audit Committee Chair",
    "Audit Committee Member"
]

# Leadership roles that can approve members
MEMBER_APPROVAL_ROLES = [
    "Chairman",
    "Secretary",
    "Branch Chairman",
    "Branch Secretary"
]

# Leadership roles that can assign roles
ROLE_ASSIGNMENT_ROLES = [
    "Chairman",
    "Secretary"
]

# Branch leadership roles
BRANCH_LEADERSHIP_ROLES = [
    "Branch Chairman", 
    "Branch Secretary"
]

# Chapter leadership roles
CHAPTER_LEADERSHIP_ROLES = [
    "Chairman",
    "Vice Chairman",
    "Secretary"
]

# All leadership roles
ALL_LEADERSHIP_ROLES = CHAPTER_LEADERSHIP_ROLES + BRANCH_LEADERSHIP_ROLES

# Permission constants
PERMISSIONS = {
    "ALL": "all",
    "READ": "read",
    "WRITE": "write", 
    "CREATE": "create",
    "UPDATE": "update",
    "DELETE": "delete",
    "APPROVE": "approve",
    "ASSIGN": "assign",
    "MANAGE": "manage"
}

# Default branch minimum members
DEFAULT_MIN_MEMBERS = 20

# Membership number format
MEMBERSHIP_NUMBER_FORMAT = "NDC-{year}-{number:04d}"

# File upload settings
ALLOWED_AVATAR_TYPES = ["image/jpeg", "image/png", "image/jpg"]
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB

# API version
API_VERSION = "v1"

# Default pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Available branches for registration
AVAILABLE_BRANCHES = [
    "Leicester Branch",
    "Leeds Branch",
    "Northampton Branch",
    "Coventry Branch",
    "Oxford Branch",
    "Bedford Branch",
    "Swindon Branch",
    "Kent Branch",
    "Luton Branch",
    "Cambridge Branch",
    "West London Branch",
    "Bristol Branch",
    "Southampton Branch",
    "North London Branch",
    "South London Branch",
    "East London Branch",
    "Milton Keynes Branch",
    "Birmingham Branch",
    "Telford Branch",
    "Glasgow Branch",
    "Manchester Branch",
    "Liverpool Branch",
    "Sheffield Branch",
    "Hull Branch",
    "Aldershot",
    "Stoke-on-Trent",
    "Wiltshire",
    "Reading",
    "Walsall",
    "Salisbury and Tidworth",
    "Chester",
    "Wolverhampton",
    "Edinburgh",
    "Cardiff",
    "Nottingham"
]

# Gender options
GENDER_OPTIONS = [
    "Male",
    "Female"
]

# Common qualification categories
QUALIFICATION_CATEGORIES = [
    "No Formal Qualification",
    "Primary Education",
    "Secondary Education/GCSE",
    "A-Levels/BTECs",
    "Undergraduate Degree",
    "Postgraduate Degree",
    "Masters Degree",
    "Doctorate/PhD",
    "Professional Certification",
    "Vocational Training",
    "Other"
]