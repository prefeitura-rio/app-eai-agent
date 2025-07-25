import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token');
  const { pathname } = request.nextUrl;

  // If the user is logged in and tries to access the login page, redirect to the homepage
  if (token && pathname === '/login') {
    return NextResponse.redirect(new URL('/', request.url));
  }

  // If the user is not logged in and is trying to access any page other than login, redirect them
  if (!token && pathname !== '/login') {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect_url', pathname); // Remember the page they wanted
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  // This matcher applies the middleware to all routes except for Next.js internal paths and static assets.
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
