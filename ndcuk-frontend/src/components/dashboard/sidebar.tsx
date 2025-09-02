'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils/cn';
import { useAuth } from '@/lib/auth/auth-context';
import {
  Users,
  UserCheck,
  Building2,
  Shield,
  Settings,
  Home,
  FileText,
  User,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  {
    name: 'Members',
    icon: Users,
    children: [
      { name: 'All Members', href: '/dashboard/members' },
      { name: 'Pending Approval', href: '/dashboard/members/pending' },
    ],
  },
  {
    name: 'Roles & Permissions',
    icon: Shield,
    children: [
      { name: 'Role Assignments', href: '/dashboard/roles/assignments' },
      { name: 'All Roles', href: '/dashboard/roles' },
    ],
  },
  {
    name: 'Branches',
    icon: Building2,
    children: [
      { name: 'All Branches', href: '/dashboard/branches' },
      { name: 'Create Branch', href: '/dashboard/branches/create' },
    ],
  },
  {
    name: 'Committees',
    icon: FileText,
    children: [
      { name: 'All Committees', href: '/dashboard/committees' },
    ],
  },
  { name: 'Profile', href: '/dashboard/profile', icon: User },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();

  return (
    <div className="bg-gray-900 text-white w-64 min-h-screen p-4 custom-scrollbar overflow-y-auto">
      <div className="flex items-center space-x-2 mb-8">
        <div className="w-8 h-8 bg-ndc-red rounded-full flex items-center justify-center">
          <span className="text-sm font-bold">NDC</span>
        </div>
        <div>
          <h1 className="text-lg font-semibold">NDC UK Dashboard</h1>
          <p className="text-xs text-gray-400">Management Portal</p>
        </div>
      </div>

      <nav className="space-y-2">
        {navigation.map((item) => {
          if (item.children) {
            return (
              <div key={item.name} className="space-y-1">
                <div className="flex items-center space-x-2 text-gray-400 text-sm font-medium px-2 py-1">
                  <item.icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </div>
                <div className="ml-6 space-y-1">
                  {item.children.map((child) => (
                    <Link
                      key={child.href}
                      href={child.href}
                      className={cn(
                        'block px-2 py-1 text-sm rounded hover:bg-gray-800 transition-colors',
                        pathname === child.href
                          ? 'bg-ndc-red text-white'
                          : 'text-gray-300 hover:text-white'
                      )}
                    >
                      {child.name}
                    </Link>
                  ))}
                </div>
              </div>
            );
          }

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center space-x-2 px-2 py-2 rounded hover:bg-gray-800 transition-colors',
                pathname === item.href
                  ? 'bg-ndc-red text-white'
                  : 'text-gray-300 hover:text-white'
              )}
            >
              <item.icon className="h-5 w-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>

      <div className="absolute bottom-4 left-4 right-4">
        <div className="bg-gray-800 p-3 rounded">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
              <UserCheck className="h-4 w-4" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name}</p>
              <p className="text-xs text-gray-400 truncate">{user?.email}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}