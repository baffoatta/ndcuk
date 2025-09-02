# NDC UK & Ireland Frontend Dashboard

A modern chapter management system built with Next.js 14, TypeScript, and Tailwind CSS for the National Democratic Congress UK & Ireland chapter.

## 🚀 Features

- **Authentication System**: Secure login/registration with JWT tokens
- **Role-based Access Control**: Executive, Admin, and Member roles
- **Member Management**: View, edit, and manage member profiles
- **Branch Management**: Create and manage chapter branches
- **Executive Dashboard**: Analytics and insights for leadership
- **Committee Management**: Organize and track committees
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **Modern UI**: Built with Radix UI components

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query (@tanstack/react-query)
- **UI Components**: Radix UI, Headless UI
- **Forms**: React Hook Form with Zod validation
- **HTTP Client**: Axios with interceptors
- **Icons**: Lucide React, Heroicons
- **Charts**: Recharts

## 📋 Prerequisites

- Node.js 18+ 
- npm or yarn
- NDC UK Backend API running on port 8001

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd ndcuk-frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Set up environment variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 4. Start the development server

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000).

## 📁 Project Structure

```
src/
├── app/                    # Next.js 14 App Router
│   ├── (auth)/            # Authentication routes
│   │   ├── login/         # Login page
│   │   └── register/      # Registration page
│   ├── (dashboard)/       # Protected dashboard routes
│   │   ├── dashboard/     # Main dashboard
│   │   ├── members/       # Member management
│   │   ├── roles/         # Role assignments
│   │   ├── branches/      # Branch management
│   │   ├── committees/    # Committee management
│   │   ├── profile/       # User profile
│   │   └── settings/      # Application settings
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx          # Home page (redirects to dashboard)
├── components/
│   ├── ui/                # Reusable UI components
│   ├── auth/              # Authentication components
│   ├── dashboard/         # Dashboard-specific components
│   ├── members/           # Member management components
│   ├── roles/             # Role management components
│   ├── branches/          # Branch management components
│   ├── committees/        # Committee components
│   └── common/            # Common components
├── lib/
│   ├── api/               # API client and endpoints
│   ├── auth/              # Authentication context and utilities
│   ├── hooks/             # Custom React hooks
│   ├── store/             # State management
│   ├── providers/         # React providers
│   └── utils.ts           # Utility functions
├── types/
│   └── index.ts           # TypeScript type definitions
└── styles/
    └── globals.css        # Additional global styles
```

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## 🔐 Authentication

The application uses JWT-based authentication with:

- **Access tokens** for API requests
- **Refresh tokens** for token renewal
- **Role-based routing** for access control
- **Protected routes** with AuthGuard component

### User Roles

1. **Executive**: Full access to all features
2. **Admin**: Administrative access to member and branch management
3. **Member**: Limited access to profile and basic features

## 🎨 Styling

The application uses Tailwind CSS with custom NDC brand colors:

```css
/* NDC Brand Colors */
--ndc-red: #dc2626;
--ndc-red-dark: #b91c1c;
--ndc-green: #059669;
--ndc-gold: #f59e0b;
```

## 📱 Responsive Design

The application is fully responsive with breakpoints:

- Mobile: `<768px`
- Tablet: `768px - 1024px`
- Desktop: `>1024px`

## 🧪 API Integration

The frontend connects to the NDC UK Backend API with:

- **Base URL**: `http://localhost:8001/api/v1`
- **Authentication**: Bearer token in Authorization header
- **Error Handling**: Centralized error responses
- **Request/Response Interceptors**: Token management

### API Endpoints

- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user
- `GET /members` - List members
- `GET /branches` - List branches
- `GET /roles` - List roles

## 🚦 Development Guidelines

### Code Style

- Use TypeScript for all files
- Follow ESLint configuration
- Use functional components with hooks
- Implement proper error handling
- Write self-documenting code

### Component Structure

```tsx
interface ComponentProps {
  // Define props with TypeScript
}

export function Component({ prop }: ComponentProps) {
  // Component logic
  return (
    <div className="tailwind-classes">
      {/* JSX content */}
    </div>
  );
}
```

### API Client Usage

```tsx
import { useQuery } from '@tanstack/react-query';
import { membersApi } from '@/lib/api';

function MembersComponent() {
  const { data: members, isLoading, error } = useQuery({
    queryKey: ['members'],
    queryFn: membersApi.getAll
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error occurred</div>;

  return <div>{/* Render members */}</div>;
}
```

## 📊 Performance

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js Image component
- **Bundle Analysis**: Use `npm run analyze` (if configured)
- **Caching**: React Query for server state caching

## 🐛 Troubleshooting

### Common Issues

1. **Port 3000 in use**: Change port in `package.json` scripts
2. **API connection failed**: Ensure backend is running on port 8001
3. **Token expired**: Clear localStorage and re-login
4. **Build errors**: Run `npm run type-check` to identify issues

### Development Tips

- Use React DevTools for component debugging
- Enable React Query DevTools in development
- Check Network tab for API request/response debugging
- Use TypeScript strict mode for better type safety

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Support

For support and questions:

- Email: tech@ndcuk.org
- Documentation: [Internal Wiki]
- Issues: [GitHub Issues]

---

**NDC UK & Ireland** - Building the future of chapter management