'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/lib/auth/auth-context';
import { authApi } from '@/lib/api/auth';
import Link from 'next/link';

const registerSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one digit'),
  full_name: z.string().min(2, 'Full name must be at least 2 characters'),
  gender: z.enum(['Male', 'Female'], { required_error: 'Please select a gender' }),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  occupation: z.string().min(1, 'Occupation is required'),
  qualification: z.string().min(1, 'Qualification is required'),
  address: z.string().min(5, 'Please enter a complete address'),
  branch_name: z.string().min(1, 'Please select a branch'),
});

type RegisterFormData = z.infer<typeof registerSchema>;

export function RegisterForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [registrationInfo, setRegistrationInfo] = useState<any>(null);
  const { register: registerUser } = useAuth();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  useEffect(() => {
    // Load registration info
    const loadRegistrationInfo = async () => {
      try {
        const info = await authApi.getRegistrationInfo();
        setRegistrationInfo(info);
      } catch (error) {
        console.error('Error loading registration info:', error);
      }
    };
    
    loadRegistrationInfo();
  }, []);

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const result = await registerUser(data);
      setSuccess(result.message);
      
      // Redirect to login after a delay
      setTimeout(() => {
        router.push('/login');
      }, 3000);
    } catch (error: any) {
      console.error('Registration error:', error);
      setError(
        error.response?.data?.detail || 
        error.message || 
        'An error occurred during registration. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (!registrationInfo) {
    return (
      <div className="flex justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-ndc-red"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Create your account</h2>
        <p className="mt-2 text-sm text-gray-600">
          Join the NDC UK & Ireland Chapter
        </p>
      </div>

      <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="text-sm text-red-700">{error}</div>
          </div>
        )}

        {success && (
          <div className="rounded-md bg-green-50 p-4">
            <div className="text-sm text-green-700">
              {success}
              <br />
              <span className="font-medium">Redirecting to login...</span>
            </div>
          </div>
        )}

        {/* Full Name */}
        <div>
          <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
            Full Name *
          </label>
          <div className="mt-1">
            <Input
              id="full_name"
              type="text"
              {...register('full_name')}
              className={errors.full_name ? 'border-red-300' : ''}
            />
            {errors.full_name && (
              <p className="mt-2 text-sm text-red-600">{errors.full_name.message}</p>
            )}
          </div>
        </div>

        {/* Email */}
        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700">
            Email Address *
          </label>
          <div className="mt-1">
            <Input
              id="email"
              type="email"
              autoComplete="email"
              {...register('email')}
              className={errors.email ? 'border-red-300' : ''}
            />
            {errors.email && (
              <p className="mt-2 text-sm text-red-600">{errors.email.message}</p>
            )}
          </div>
        </div>

        {/* Password */}
        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700">
            Password *
          </label>
          <div className="mt-1">
            <Input
              id="password"
              type="password"
              autoComplete="new-password"
              {...register('password')}
              className={errors.password ? 'border-red-300' : ''}
            />
            {errors.password && (
              <p className="mt-2 text-sm text-red-600">{errors.password.message}</p>
            )}
          </div>
        </div>

        {/* Gender */}
        <div>
          <label htmlFor="gender" className="block text-sm font-medium text-gray-700">
            Gender *
          </label>
          <div className="mt-1">
            <select
              id="gender"
              {...register('gender')}
              className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-ndc-red focus:ring-ndc-red ${
                errors.gender ? 'border-red-300' : ''
              }`}
            >
              <option value="">Select Gender</option>
              {registrationInfo.gender_options.map((gender: string) => (
                <option key={gender} value={gender}>
                  {gender}
                </option>
              ))}
            </select>
            {errors.gender && (
              <p className="mt-2 text-sm text-red-600">{errors.gender.message}</p>
            )}
          </div>
        </div>

        {/* Date of Birth */}
        <div>
          <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700">
            Date of Birth *
          </label>
          <div className="mt-1">
            <Input
              id="date_of_birth"
              type="date"
              {...register('date_of_birth')}
              className={errors.date_of_birth ? 'border-red-300' : ''}
            />
            {errors.date_of_birth && (
              <p className="mt-2 text-sm text-red-600">{errors.date_of_birth.message}</p>
            )}
          </div>
        </div>

        {/* Occupation */}
        <div>
          <label htmlFor="occupation" className="block text-sm font-medium text-gray-700">
            Occupation *
          </label>
          <div className="mt-1">
            <Input
              id="occupation"
              type="text"
              {...register('occupation')}
              className={errors.occupation ? 'border-red-300' : ''}
            />
            {errors.occupation && (
              <p className="mt-2 text-sm text-red-600">{errors.occupation.message}</p>
            )}
          </div>
        </div>

        {/* Qualification */}
        <div>
          <label htmlFor="qualification" className="block text-sm font-medium text-gray-700">
            Qualification *
          </label>
          <div className="mt-1">
            <select
              id="qualification"
              {...register('qualification')}
              className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-ndc-red focus:ring-ndc-red ${
                errors.qualification ? 'border-red-300' : ''
              }`}
            >
              <option value="">Select Qualification</option>
              {registrationInfo.qualification_categories.map((qual: string) => (
                <option key={qual} value={qual}>
                  {qual}
                </option>
              ))}
            </select>
            {errors.qualification && (
              <p className="mt-2 text-sm text-red-600">{errors.qualification.message}</p>
            )}
          </div>
        </div>

        {/* Address */}
        <div>
          <label htmlFor="address" className="block text-sm font-medium text-gray-700">
            House Address *
          </label>
          <div className="mt-1">
            <Input
              id="address"
              type="text"
              {...register('address')}
              className={errors.address ? 'border-red-300' : ''}
              placeholder="Full address including city and postcode"
            />
            {errors.address && (
              <p className="mt-2 text-sm text-red-600">{errors.address.message}</p>
            )}
          </div>
        </div>

        {/* Branch */}
        <div>
          <label htmlFor="branch_name" className="block text-sm font-medium text-gray-700">
            Branch *
          </label>
          <div className="mt-1">
            <select
              id="branch_name"
              {...register('branch_name')}
              className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-ndc-red focus:ring-ndc-red ${
                errors.branch_name ? 'border-red-300' : ''
              }`}
            >
              <option value="">Select Branch</option>
              {registrationInfo.available_branches.map((branch: string) => (
                <option key={branch} value={branch}>
                  {branch}
                </option>
              ))}
            </select>
            {errors.branch_name && (
              <p className="mt-2 text-sm text-red-600">{errors.branch_name.message}</p>
            )}
          </div>
        </div>

        <div>
          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Creating account...' : 'Create account'}
          </Button>
        </div>

        <div className="text-center">
          <span className="text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="font-medium text-ndc-red hover:text-ndc-red-dark">
              Sign in here
            </Link>
          </span>
        </div>
      </form>
    </div>
  );
}