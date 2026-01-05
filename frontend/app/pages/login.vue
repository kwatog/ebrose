<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const { success, error: showError } = useToast()

const form = ref({
  username: '',
  password: ''
})
const loading = ref(false)

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

const login = async () => {
  loading.value = true
  
  try {
    const response = await $fetch<{message: string, user: any}>(`${apiBase}/auth/login`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        username: form.value.username,
        password: form.value.password
      })
    })
    
    // The backend sets cookies (access_token and user_info) in the response
    // We need to ensure the frontend sees them before navigating
    // useCookie needs to sync with the browser's cookies
    const userCookie = useCookie('user_info', { default: () => null })
    
    // Wait for the cookie to be set by the backend response
    // The cookie should be available in document.cookie after the fetch
    let attempts = 0
    while (!userCookie.value && attempts < 20) {
      await new Promise(resolve => setTimeout(resolve, 50))
      attempts++
    }
    
    // If still no cookie (e.g., HttpOnly), manually set from response data
    if (!userCookie.value && response.user) {
      const userData = response.user
      const userInfoStr = JSON.stringify({
        id: userData.id,
        username: userData.username,
        full_name: userData.full_name,
        role: userData.role,
        department: userData.department,
      })
      userCookie.value = btoa(unescape(encodeURIComponent(userInfoStr)))
    }

    success('Login successful!')
    
    // Use replace: true to avoid history stack issues
    await navigateTo('/', { replace: true, redirectCode: 302 })
  } catch (e: any) {
    showError(e.data?.detail || 'Login failed')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <BaseCard padding="lg" class="login-card">
      <h1 class="card-title">Welcome to Ebrose</h1>
      <p class="card-sub">Please sign in to continue</p>

      <form @submit.prevent="login" class="login-form">
        <BaseInput
          id="username"
          v-model="form.username"
          type="text"
          label="Username"
          placeholder="Enter your username"
          required
        />

        <BaseInput
          id="password"
          v-model="form.password"
          type="password"
          label="Password"
          placeholder="Enter your password"
          required
        />

        <BaseButton
          type="submit"
          variant="primary"
          :loading="loading"
          :full-width="true"
          class="login-btn"
        >
          Sign In
        </BaseButton>
      </form>
    </BaseCard>
  </div>
</template>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gray-50);
}

.login-card {
  width: 100%;
  max-width: 420px;
}

.card-title {
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--color-gray-900);
  margin: 0 0 var(--spacing-2);
}

.card-sub {
  font-size: var(--text-base);
  color: var(--color-gray-500);
  margin: 0 0 var(--spacing-6);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.login-btn {
  margin-top: var(--spacing-2);
}
</style>
