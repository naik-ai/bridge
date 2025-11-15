/**
 * Authentication utilities
 * Handles Google OAuth flow and session management
 */

export interface User {
  id: string
  email: string
  name: string
  picture?: string
}

/**
 * Get the current user from session
 * In production, this would fetch from the backend API
 */
export async function getCurrentUser(): Promise<User | null> {
  // TODO: Implement actual session check with backend
  // For now, return null (unauthenticated)
  return null
}

/**
 * Sign in with Google OAuth
 */
export async function signInWithGoogle(returnUrl?: string): Promise<void> {
  // TODO: Redirect to Google OAuth flow
  // const url = returnUrl ? `/api/auth/google?returnUrl=${encodeURIComponent(returnUrl)}` : '/api/auth/google'
  // window.location.href = url
  console.log('Sign in with Google - not yet implemented', { returnUrl })
}

/**
 * Initiate login flow
 * Alias for signInWithGoogle for compatibility
 */
export const initiateLogin = signInWithGoogle

/**
 * Sign out current user
 */
export async function signOut(): Promise<void> {
  // TODO: Call backend signout endpoint
  // await fetch('/api/auth/signout', { method: 'POST' })
  console.log('Sign out - not yet implemented')
}

/**
 * Logout function
 * Alias for signOut for compatibility
 */
export const logout = signOut
