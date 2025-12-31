export default defineNuxtRouteMiddleware(async (to) => {
  const userInfoCookie = useCookie('user_info')

  let userInfo = null
  if (userInfoCookie.value) {
    try {
      userInfo = JSON.parse(atob(userInfoCookie.value))
    } catch {
      userInfo = null
    }
  }

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
    if (refreshedCookie.value) {
      try {
        userInfo = JSON.parse(atob(refreshedCookie.value))
      } catch {
        userInfo = null
      }
    }
  }

  if (!userInfo) {
    return navigateTo('/login')
  }
})
