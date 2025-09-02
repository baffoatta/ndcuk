import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Page Not Found</h2>
        <p className="text-gray-600 mb-6">Could not find requested resource</p>
        <Link
          href="/dashboard"
          className="bg-ndc-red text-white px-4 py-2 rounded-md hover:bg-ndc-red-dark transition-colors"
        >
          Return Home
        </Link>
      </div>
    </div>
  );
}