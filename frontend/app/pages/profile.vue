<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase

const userCookie = useCookie('user_info')
const tokenCookie = useCookie('access_token')
const { success, error: showError } = useToast()

// Safe user data parsing
const userData = ref<Record<string, any> | null>(null)

onMounted(() => {
  if (userCookie.value) {
    try {
      const cookieStr = String(userCookie.value).replace(/"/g, '')
      const decoded = decodeURIComponent(atob(cookieStr))
      userData.value = JSON.parse(decoded)
    } catch {
      userData.value = null
    }
  }
})

// Computed for template access
const user = computed(() => userData.value)

const profileForm = ref({
  full_name: '',
  department: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: ''
})

// Initialize form when user data is available
watch(userData, (newUser) => {
  if (newUser) {
    profileForm.value = {
      full_name: newUser.full_name || '',
      department: newUser.department || ''
    }
  }
}, { immediate: true })

const loading = ref(false)
const passwordLoading = ref(false)

const updateProfile = async () => {
  loading.value = true
  try {
    const response = await $fetch(`${apiBase}/auth/me`, {
      method: 'PUT',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profileForm.value)
    })
    success('Profile updated successfully')
  } catch (e: any) {
    showError(e.data?.detail || 'Failed to update profile')
  } finally {
    loading.value = false
  }
}

const changePassword = async () => {
  passwordLoading.value = true
  try {
    await $fetch(`${apiBase}/auth/password`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(passwordForm.value)
    })
    success('Password changed successfully')
    passwordForm.value = { current_password: '', new_password: '' }
  } catch (e: any) {
    const errorMessage = e.response?._data?.detail || e.data?.detail || e.message || 'Failed to change password'
    showError(errorMessage)
  } finally {
    passwordLoading.value = false
  }
}
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">Profile Settings</h1>
      <p class="page-subtitle">Manage your account information and password</p>
    </div>

    <div class="profile-grid">
      <BaseCard padding="lg" class="profile-card">
        <h2 class="card-title">Profile Information</h2>
        <p class="card-sub">Update your personal details</p>

        <form @submit.prevent="updateProfile" class="profile-form">
          <BaseInput
            id="username"
            :model-value="userData?.username || ''"
            type="text"
            label="Username"
            disabled
          />
          <BaseInput
            id="email"
            :model-value="userData?.email || ''"
            type="email"
            label="Email"
            disabled
          />

          <BaseInput
            id="full_name"
            v-model="profileForm.full_name"
            type="text"
            label="Full Name"
            placeholder="Enter your full name"
          />

          <BaseInput
            id="department"
            v-model="profileForm.department"
            type="text"
            label="Department"
            placeholder="Enter your department"
          />

          <BaseInput
            id="role"
            :model-value="userData?.role || ''"
            type="text"
            label="Role"
            disabled
          />

          <BaseButton type="submit" :loading="loading" class="save-btn">
            Save Changes
          </BaseButton>
        </form>
      </BaseCard>

      <BaseCard padding="lg" class="password-card">
        <h2 class="card-title">Change Password</h2>
        <p class="card-sub">Update your password to keep your account secure</p>

        <form @submit.prevent="changePassword" class="password-form">
          <BaseInput
            id="current_password"
            v-model="passwordForm.current_password"
            type="password"
            label="Current Password"
            placeholder="Enter current password"
            required
          />

          <PasswordStrength v-model="passwordForm.new_password" />

          <BaseButton 
            type="submit" 
            :loading="passwordLoading"
            :disabled="passwordForm.new_password.length < 8"
            class="change-btn"
          >
            Change Password
          </BaseButton>
        </form>
      </BaseCard>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-6);
}

.page-header {
  margin-bottom: var(--spacing-6);
}

.page-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-gray-900);
  margin: 0;
}

.page-subtitle {
  color: var(--color-gray-500);
  margin: var(--spacing-1) 0 0 0;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: var(--spacing-6);
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-gray-900);
  margin: 0;
}

.card-sub {
  color: var(--color-gray-500);
  font-size: var(--text-sm);
  margin: var(--spacing-1) 0 var(--spacing-6) 0;
}

.profile-form,
.password-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.save-btn,
.change-btn {
  margin-top: var(--spacing-2);
  width: 100%;
}

@media (max-width: 900px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
