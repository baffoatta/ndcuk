'use client';

import { useAuth } from './auth-context';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface AuthGuardProps {
  children: React.ReactNode;
  requiredPermission?: string;
  fallback?: React.ReactNode;
}

export function AuthGuard({ children, requiredPermission, fallback }: AuthGuardProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-ndc-red"></div>
      </div>
    );
  }

  // Not authenticated, redirect is happening
  if (!isAuthenticated) {
    return null;
  }

  // Check for specific permissions if required
  if (requiredPermission) {
    // TODO: Implement permission checking logic
    // For now, just check if user exists
    if (!user) {
      return fallback || <div className="text-center py-8 text-red-600">Access denied</div>;
    }
  }

  return <>{children}</>;
}