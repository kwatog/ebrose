export default defineNuxtRouteMiddleware(async (to) => {
  // Only run on client side - cookies aren't available during SSR
  if (import.meta.server) return

  const userInfoCookie = useCookie('user_info')

  const decodeUserInfo = (value: any): any => {
    if (!value) return null
    // If value is already an object (from client-side setting), return it directly
    if (typeof value === 'object') return value
    try {
      let b64 = String(value)
      if (b64.startsWith('"') && b64.endsWith('"')) {
        b64 = b64.slice(1, -1)
      }
      const json = decodeURIComponent(escape(atob(b64)))
      return JSON.parse(json)
    } catch {
      return null
    }
  }

  let userInfo = decodeUserInfo(userInfoCookie.value)

  const publicPaths = new Set(['/login', '/health'])
  if (publicPaths.has(to.path)) return

  // If no user info, try to refresh token
  if (!userInfo) {
    const config = useRuntimeConfig()
    const apiBase = config.public.apiBase
    try {
      await $fetch(`${apiBase}/auth/refresh`, {
        method: 'POST',
        credentials: 'include'
      })
      // Refresh succeeded, get updated cookie
      userInfo = decodeUserInfo(userInfoCookie.value)
    } catch {
      // Refresh failed, continue with null userInfo
    }
  }

  // Final check - if still no user info, redirect to login
  if (!userInfo) {
    return navigateTo('/login')
  }
})
