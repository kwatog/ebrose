export default defineNuxtRouteMiddleware(async (to) => {
  const userInfoCookie = useCookie('user_info')

  const decodeUserInfo = (value: string | null): any => {
    if (!value) return null
    try {
      let b64 = value
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

  if (!userInfo) {
    const config = useRuntimeConfig()
    const apiBase = (config as any).apiBase || config.public.apiBase
    try {
      await $fetch(`${apiBase}/auth/refresh`, {
        method: 'POST',
        credentials: 'include'
      })
    } catch {
    }
  }

  if (!userInfo) {
    const refreshedCookie = useCookie('user_info')
    userInfo = decodeUserInfo(refreshedCookie.value)
  }

  if (!userInfo) {
    return navigateTo('/login')
  }
})
