'use client';

import { useAuth } from '@/lib/auth/auth-context';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Users, UserCheck, Building2, Shield } from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuth();

  // Mock data - would come from API in real implementation
  const stats = [
    {
      title: 'Total Members',
      value: '2,547',
      change: '+12.5%',
      icon: Users,
      color: 'bg-blue-500',
    },
    {
      title: 'Active Members',
      value: '2,341',
      change: '+4.8%',
      icon: UserCheck,
      color: 'bg-green-500',
    },
    {
      title: 'Active Branches',
      value: '35',
      change: '+2',
      icon: Building2,
      color: 'bg-purple-500',
    },
    {
      title: 'Executives',
      value: '127',
      change: '+8',
      icon: Shield,
      color: 'bg-ndc-red',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Welcome back, {user?.full_name}!
        </h1>
        <p className="text-gray-600">
          Here&apos;s what&apos;s happening with your chapter today.
        </p>
        {user?.membership_number && (
          <p className="text-sm text-gray-500 mt-2">
            Membership: <span className="font-mono">{user.membership_number}</span>
          </p>
        )}
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <div className={`w-8 h-8 rounded-full ${stat.color} flex items-center justify-center`}>
                  <Icon className="h-4 w-4 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-gray-600">
                  <span className="text-green-600">{stat.change}</span> from last month
                </p>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest updates from your chapter</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">New member approved</p>
                  <p className="text-xs text-gray-500">Sarah Johnson joined Manchester Branch</p>
                  <p className="text-xs text-gray-400">2 hours ago</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">Role assignment updated</p>
                  <p className="text-xs text-gray-500">John Smith appointed as Branch Secretary</p>
                  <p className="text-xs text-gray-400">1 day ago</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">New branch created</p>
                  <p className="text-xs text-gray-500">Reading Branch established</p>
                  <p className="text-xs text-gray-400">3 days ago</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks you might need</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              <button className="p-3 text-left rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                <UserCheck className="h-5 w-5 text-green-600 mb-2" />
                <p className="font-medium text-sm">Approve Members</p>
                <p className="text-xs text-gray-500">Review pending applications</p>
              </button>
              
              <button className="p-3 text-left rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                <Shield className="h-5 w-5 text-blue-600 mb-2" />
                <p className="font-medium text-sm">Assign Roles</p>
                <p className="text-xs text-gray-500">Manage executive positions</p>
              </button>
              
              <button className="p-3 text-left rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                <Building2 className="h-5 w-5 text-purple-600 mb-2" />
                <p className="font-medium text-sm">Branch Management</p>
                <p className="text-xs text-gray-500">Create or manage branches</p>
              </button>
              
              <button className="p-3 text-left rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors">
                <Users className="h-5 w-5 text-ndc-red mb-2" />
                <p className="font-medium text-sm">View Reports</p>
                <p className="text-xs text-gray-500">Membership analytics</p>
              </button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}