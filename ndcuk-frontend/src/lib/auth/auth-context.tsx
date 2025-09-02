'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, AuthResponse } from '@/types/auth';
import { authApi } from '@/lib/api/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: any) => Promise<{ message: string }>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const userData = await authApi.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      // Token might be expired, clear it
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response: AuthResponse = await authApi.login({ email, password });
    
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('refresh_token', response.refresh_token);
    
    // Get user data after successful login
    const userData = await authApi.getCurrentUser();
    setUser(userData);
  };

  const register = async (userData: any) => {
    const response = await authApi.register(userData);
    // Registration successful, but user needs to verify email first
    return response;
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      // Even if API call fails, clear local data
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  const refreshToken = async () => {
    try {
      const refreshTokenValue = localStorage.getItem('refresh_token');
      if (!refreshTokenValue) throw new Error('No refresh token');

      const response = await authApi.refreshToken({ refresh_token: refreshTokenValue });
      
      localStorage.setItem('access_token', response.access_token);
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }
      
      if (response.user) {
        setUser(response.user);
      }
    } catch (error) {
      await logout();
    }
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}