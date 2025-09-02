import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-ndc-red rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-xl">NDC</span>
          </div>
        </div>
        <h1 className="mt-6 text-center text-3xl font-bold tracking-tight text-gray-900">
          NDC UK & Ireland
        </h1>
        <p className="mt-2 text-center text-sm text-gray-600">
          Chapter Management System
        </p>
      </div>
      
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {children}
        </div>
      </div>
    </div>
  );
}