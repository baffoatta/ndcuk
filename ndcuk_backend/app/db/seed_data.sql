-- NDC UK Backend Seed Data
-- Insert role categories
INSERT INTO role_categories (name, description, sort_order) VALUES
('Chapter Executives', 'Core chapter-level executive positions', 1),
('Branch Executives', 'Branch-level executive positions', 2),
('Committees', 'Chapter-level committee positions', 3),
('Special Roles', 'Special electoral and temporary roles', 4);

-- Insert default chapter
INSERT INTO chapters (name, country, description) VALUES 
('NDC UK & Ireland', 'UK', 'National Democratic Congress UK and Ireland Chapter');

-- Get chapter ID for subsequent inserts
WITH chapter_data AS (
  SELECT id as chapter_id FROM chapters WHERE name = 'NDC UK & Ireland'
)
-- Insert sample branches
INSERT INTO branches (chapter_id, name, location, description) 
SELECT chapter_id, 'London Central', 'London', 'Central London Branch' FROM chapter_data
UNION ALL
SELECT chapter_id, 'Manchester', 'Manchester', 'Manchester Branch' FROM chapter_data
UNION ALL  
SELECT chapter_id, 'Birmingham', 'Birmingham', 'Birmingham Branch' FROM chapter_data;

-- Insert Chapter-Level Executive Roles
INSERT INTO roles (name, scope_type, description, permissions, category_id) 
SELECT 
  role_name,
  'chapter',
  role_desc,
  role_perms::jsonb,
  (SELECT id FROM role_categories WHERE name = 'Chapter Executives')
FROM (VALUES
  ('Chairman', 'Chapter Chairman - Overall leadership and superuser privileges', '{"all": true}'),
  ('Vice Chairman', 'Chapter Vice Chairman - Deputy leadership', '{"chapter": ["read", "write"], "branches": ["read", "write"], "members": ["read", "write"]}'),
  ('Secretary', 'Chapter Secretary - Records, correspondence, committee creation', '{"chapter": ["read", "write"], "committees": ["create", "manage"], "members": ["read", "write"], "meetings": ["read", "write"]}'),
  ('Assistant Secretary', 'Chapter Assistant Secretary - Support role', '{"chapter": ["read"], "members": ["read", "write"], "meetings": ["read", "write"]}'),
  ('Treasurer', 'Chapter Treasurer - Financial management', '{"finance": ["read", "write"], "payments": ["read", "write"], "members": ["read"]}'),
  ('Assistant Treasurer', 'Chapter Assistant Treasurer - Financial support', '{"finance": ["read"], "payments": ["read"], "members": ["read"]}'),
  ('Organiser', 'Chapter Organiser - Events and mobilization', '{"events": ["read", "write"], "mobilization": ["read", "write"], "members": ["read"]}'),
  ('Deputy Organiser', 'Chapter Deputy Organiser - Support organizing', '{"events": ["read", "write"], "mobilization": ["read"], "members": ["read"]}'),
  ('Youth Organiser', 'Chapter Youth Organiser - Youth engagement', '{"events": ["read", "write"], "youth": ["read", "write"], "members": ["read"]}'),
  ('Deputy Youth Organiser', 'Chapter Deputy Youth Organiser - Youth support', '{"events": ["read"], "youth": ["read", "write"], "members": ["read"]}'),
  ('Women''s Organiser', 'Chapter Women''s Organiser - Women''s engagement', '{"events": ["read", "write"], "women": ["read", "write"], "members": ["read"]}'),
  ('Deputy Women''s Organiser', 'Chapter Deputy Women''s Organiser - Women''s support', '{"events": ["read"], "women": ["read", "write"], "members": ["read"]}'),
  ('Public Relations Officer (PRO)', 'Chapter PRO - Communications and publicity', '{"announcements": ["read", "write"], "press": ["read", "write"], "communications": ["read", "write"]}'),
  ('Deputy PRO', 'Chapter Deputy PRO - Communications support', '{"announcements": ["read"], "press": ["read"], "communications": ["read", "write"]}'),
  ('Welfare Officer', 'Chapter Welfare Officer - Member welfare and care', '{"welfare": ["read", "write"], "members": ["read", "write"], "events": ["read"]}')
) AS t(role_name, role_desc, role_perms);

-- Insert Branch-Level Executive Roles
INSERT INTO roles (name, scope_type, description, permissions, category_id)
SELECT 
  role_name,
  'branch',
  role_desc,
  role_perms::jsonb,
  (SELECT id FROM role_categories WHERE name = 'Branch Executives')
FROM (VALUES
  ('Branch Chairman', 'Branch Chairman - Branch leadership and member approval', '{"branch": ["all"], "members": ["read", "write", "approve"], "events": ["read", "write"]}'),
  ('Branch Secretary', 'Branch Secretary - Branch records and correspondence', '{"branch": ["read", "write"], "members": ["read", "write", "approve"], "meetings": ["read", "write"]}'),
  ('Branch Treasurer', 'Branch Treasurer - Branch financial management', '{"branch_finance": ["read", "write"], "payments": ["read"], "members": ["read"]}'),
  ('Branch Organiser', 'Branch Organiser - Branch events and mobilization', '{"branch_events": ["read", "write"], "mobilization": ["read", "write"], "members": ["read"]}'),
  ('Branch Youth Organiser', 'Branch Youth Organiser - Branch youth engagement', '{"branch_events": ["read", "write"], "youth": ["read", "write"], "members": ["read"]}'),
  ('Branch Women''s Organiser', 'Branch Women''s Organiser - Branch women''s engagement', '{"branch_events": ["read", "write"], "women": ["read", "write"], "members": ["read"]}'),
  ('Branch Welfare Officer', 'Branch Welfare Officer - Branch member welfare', '{"welfare": ["read", "write"], "members": ["read", "write"], "branch_events": ["read"]}'),
  ('Branch PRO', 'Branch PRO - Branch communications (requires chapter approval)', '{"announcements": ["read", "draft"], "communications": ["read", "write"]}'),
  ('Branch Executive Member', 'Branch Executive Member - Special duties', '{"members": ["read"], "branch_events": ["read"], "meetings": ["read"]}')
) AS t(role_name, role_desc, role_perms);

-- Insert Committee Roles (Chapter Level)
INSERT INTO roles (name, scope_type, description, permissions, category_id)
SELECT 
  role_name,
  'chapter',
  role_desc,
  role_perms::jsonb,
  (SELECT id FROM role_categories WHERE name = 'Committees')
FROM (VALUES
  ('Finance Committee Chair', 'Finance Committee Chairman', '{"finance": ["read", "write"], "committees": ["finance_committee"], "reports": ["read", "write"]}'),
  ('Finance Committee Member', 'Finance Committee Member', '{"finance": ["read"], "committees": ["finance_committee"], "reports": ["read"]}'),
  ('Public Relations Committee Chair', 'PR Committee Chairman', '{"pr": ["read", "write"], "committees": ["pr_committee"], "communications": ["read", "write"]}'),
  ('Public Relations Committee Member', 'PR Committee Member', '{"pr": ["read"], "committees": ["pr_committee"], "communications": ["read"]}'),
  ('Research Committee Chair', 'Research Committee Chairman', '{"research": ["read", "write"], "committees": ["research_committee"], "reports": ["read", "write"]}'),
  ('Research Committee Member', 'Research Committee Member', '{"research": ["read"], "committees": ["research_committee"], "reports": ["read"]}'),
  ('Organisation Committee Chair', 'Organisation Committee Chairman', '{"organisation": ["read", "write"], "committees": ["org_committee"], "mobilization": ["read", "write"]}'),
  ('Organisation Committee Member', 'Organisation Committee Member', '{"organisation": ["read"], "committees": ["org_committee"], "mobilization": ["read"]}'),
  ('Welfare Committee Chair', 'Welfare Committee Chairman', '{"welfare": ["read", "write"], "committees": ["welfare_committee"], "members": ["read", "write"]}'),
  ('Welfare Committee Member', 'Welfare Committee Member', '{"welfare": ["read"], "committees": ["welfare_committee"], "members": ["read"]}'),
  ('Complaints Committee Chair', 'Complaints Committee Chairman', '{"complaints": ["read", "write", "investigate"], "committees": ["complaints_committee"], "disciplinary": ["read"]}'),
  ('Complaints Committee Member', 'Complaints Committee Member', '{"complaints": ["read", "investigate"], "committees": ["complaints_committee"]}'),
  ('Disciplinary Committee Chair', 'Disciplinary Committee Chairman', '{"disciplinary": ["read", "write", "decide"], "committees": ["disciplinary_committee"], "members": ["suspend", "expel"]}'),
  ('Disciplinary Committee Member', 'Disciplinary Committee Member', '{"disciplinary": ["read", "decide"], "committees": ["disciplinary_committee"]}'),
  ('Audit Committee Chair', 'Audit Committee Chairman', '{"audit": ["read", "write"], "committees": ["audit_committee"], "finance": ["read", "audit"]}'),
  ('Audit Committee Member', 'Audit Committee Member', '{"audit": ["read"], "committees": ["audit_committee"], "finance": ["read"]}')
) AS t(role_name, role_desc, role_perms);

-- Insert Special Electoral Role
INSERT INTO roles (name, scope_type, description, permissions, category_id) VALUES
('Electoral Commissioner', 'both', 'Electoral Commissioner - Election supervision and management', 
 '{"elections": ["read", "write", "supervise"], "voting": ["manage"], "candidates": ["read", "write"], "electoral_roles": ["assign"]}'::jsonb,
 (SELECT id FROM role_categories WHERE name = 'Special Roles'));