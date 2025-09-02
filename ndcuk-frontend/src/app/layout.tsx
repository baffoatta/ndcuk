import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { AuthProvider } from '@/lib/auth/auth-context';
import { QueryProvider } from '@/lib/providers/query-provider';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'NDC UK Dashboard',
  description: 'National Democratic Congress UK & Ireland Chapter Management System',
  keywords: ['NDC', 'Ghana', 'UK', 'Ireland', 'Politics', 'Dashboard'],
  authors: [{ name: 'NDC UK' }],
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <QueryProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}