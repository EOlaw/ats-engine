import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const PROTECTED_PREFIXES = [
  '/dashboard',
  '/resume',
  '/billing',
  '/account',
]

const AUTH_PATHS = ['/login', '/register', '/forgot-password']

export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl

  const isProtected = PROTECTED_PREFIXES.some((prefix) => pathname.startsWith(prefix))
  const isAuthPath = AUTH_PATHS.some((p) => pathname.startsWith(p))

  // Check for auth token in cookies (set by client on login)
  const token = request.cookies.get('ats_access_token')?.value

  if (isProtected && !token) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (isAuthPath && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/resume/:path*',
    '/billing/:path*',
    '/account/:path*',
    '/login',
    '/register',
    '/forgot-password',
  ],
}
