/**
 * Next.js Middleware
 *
 * Route protection based on session_token cookie.
 */

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// Public routes that don't require authentication
const PUBLIC_ROUTES = ['/', '/login'];

// Routes that should redirect authenticated users away
const AUTH_ROUTES = ['/login'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const sessionToken = request.cookies.get('session_token');
  const isAuthenticated = !!sessionToken;

  // Allow public routes
  if (PUBLIC_ROUTES.includes(pathname)) {
    // Redirect authenticated users away from login page
    if (isAuthenticated && AUTH_ROUTES.includes(pathname)) {
      return NextResponse.redirect(new URL('/dashboards', request.url));
    }
    return NextResponse.next();
  }

  // Protect all other routes
  if (!isAuthenticated) {
    const loginUrl = new URL('/login', request.url);
    // Preserve the intended destination
    if (pathname !== '/') {
      loginUrl.searchParams.set('returnUrl', pathname);
    }
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

// Configure middleware to run on all routes except static files and API routes
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public directory)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\..*|api).*)',
  ],
};
