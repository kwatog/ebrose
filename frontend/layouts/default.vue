<script setup lang="ts">
const userCookie = useCookie('user_info')
const tokenCookie = useCookie('access_token')

const decodeUserInfo = (value: string | null | object): any => {
  if (!value) return null
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

const user = ref(decodeUserInfo(userCookie.value))

watch(userCookie, (newVal) => {
  user.value = decodeUserInfo(newVal)
})

const logout = async () => {
  tokenCookie.value = null
  userCookie.value = null
  user.value = null
  await navigateTo('/login')
}

const isAdminOrManager = computed(() => {
  return user.value && ['Admin', 'Manager'].includes(user.value.role)
})

const isActive = (path: string) => {
  if (path === '/') {
    return useRoute().path === '/'
  }
  return useRoute().path.startsWith(path)
}
</script>

<template>
  <div>
    <header class="header" v-if="$route.path !== '/login'">
      <div class="header-left">
        <NuxtLink to="/" class="logo">
          <span class="logo-icon">📊</span>
          <div class="logo-text">
            <span class="logo-title">Ebrose</span>
            <span class="logo-sub">Chamber of Spend Records</span>
          </div>
        </NuxtLink>
      </div>
      
      <nav class="nav-main">
        <div class="nav-section">
          <NuxtLink to="/" class="nav-link" :class="{ active: isActive('/') && $route.path === '/' }">
            <span class="nav-icon">🏠</span>
            <span class="nav-label">Dashboard</span>
          </NuxtLink>
          
          <div class="nav-dropdown">
            <button class="nav-link nav-dropdown-trigger">
              <span class="nav-icon">💰</span>
              <span class="nav-label">Finance</span>
              <span class="nav-arrow">▼</span>
            </button>
            <div class="nav-dropdown-menu">
              <NuxtLink to="/budget-items" class="nav-dropdown-item">Budget Items</NuxtLink>
              <NuxtLink to="/business-cases" class="nav-dropdown-item">Business Cases</NuxtLink>
              <NuxtLink to="/line-items" class="nav-dropdown-item">Line Items</NuxtLink>
            </div>
          </div>
          
          <div class="nav-dropdown">
            <button class="nav-link nav-dropdown-trigger">
              <span class="nav-icon">📁</span>
              <span class="nav-label">Projects</span>
              <span class="nav-arrow">▼</span>
            </button>
            <div class="nav-dropdown-menu">
              <NuxtLink to="/wbs" class="nav-dropdown-item">WBS</NuxtLink>
              <NuxtLink to="/assets" class="nav-dropdown-item">Assets</NuxtLink>
              <NuxtLink to="/purchase-orders" class="nav-dropdown-item">Purchase Orders</NuxtLink>
              <NuxtLink to="/goods-receipts" class="nav-dropdown-item">Goods Receipts</NuxtLink>
            </div>
          </div>
          
          <NuxtLink to="/resources" class="nav-link" :class="{ active: isActive('/resources') }">
            <span class="nav-icon">👥</span>
            <span class="nav-label">Resources</span>
          </NuxtLink>
          
          <NuxtLink to="/allocations" class="nav-link" :class="{ active: isActive('/allocations') }">
            <span class="nav-icon">📊</span>
            <span class="nav-label">Allocations</span>
          </NuxtLink>
        </div>
        
        <div class="nav-section nav-section-right">
          <template v-if="isAdminOrManager">
            <div class="nav-dropdown">
              <button class="nav-link nav-dropdown-trigger admin-trigger">
                <span class="nav-icon">⚙️</span>
                <span class="nav-label">Admin</span>
                <span class="nav-arrow">▼</span>
              </button>
              <div class="nav-dropdown-menu nav-dropdown-right">
                <NuxtLink to="/admin/groups" class="nav-dropdown-item">User Groups</NuxtLink>
                <NuxtLink to="/admin/audit" class="nav-dropdown-item">Audit Logs</NuxtLink>
              </div>
            </div>
          </template>
          
          <div class="user-section">
            <div class="user-avatar">{{ user?.username?.charAt(0)?.toUpperCase() || '?' }}</div>
            <div class="user-info">
              <span class="user-name">{{ user?.username }}</span>
              <span class="user-role">{{ user?.role }}</span>
            </div>
            <button @click="logout" class="logout-btn" title="Logout">
              <span>🚪</span>
            </button>
          </div>
        </div>
      </nav>
    </header>
    <main class="main-container">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 0 1.5rem;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: inherit;
}

.logo-icon {
  font-size: 1.75rem;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  line-height: 1.2;
}

.logo-sub {
  font-size: 0.7rem;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.nav-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex: 1;
  margin-left: 2rem;
  height: 100%;
}

.nav-section {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  height: 100%;
}

.nav-section-right {
  gap: 0.5rem;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  text-decoration: none;
  color: #4b5563;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
  background: none;
  cursor: pointer;
}

.nav-link:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.nav-link.active {
  background: #eff6ff;
  color: #2563eb;
}

.nav-icon {
  font-size: 1rem;
}

.nav-label {
  display: none;
}

.nav-arrow {
  font-size: 0.6rem;
  margin-left: 0.25rem;
  opacity: 0.6;
}

.nav-dropdown {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
}

.nav-dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 200px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
  padding: 0.5rem;
  opacity: 0;
  visibility: hidden;
  transform: translateY(10px);
  transition: all 0.2s;
  margin-top: 0.5rem;
}

.nav-dropdown:hover .nav-dropdown-menu,
.nav-dropdown-trigger:focus + .nav-dropdown-menu {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.nav-dropdown-right {
  left: auto;
  right: 0;
}

.nav-dropdown-item {
  display: block;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: #4b5563;
  font-size: 0.9rem;
  transition: all 0.15s;
}

.nav-dropdown-item:hover {
  background: #f3f4f6;
  color: #1f2937;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding-left: 1rem;
  border-left: 1px solid #e5e7eb;
  margin-left: 0.5rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1f2937;
}

.user-role {
  font-size: 0.75rem;
  color: #9ca3af;
}

.logout-btn {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1rem;
}

.logout-btn:hover {
  background: #fee2e2;
}

@media (min-width: 768px) {
  .nav-label {
    display: inline;
  }
  
  .nav-link {
    padding: 0.5rem 1rem;
  }
}

@media (max-width: 767px) {
  .header {
    padding: 0 1rem;
  }
  
  .logo-sub {
    display: none;
  }
  
  .nav-section-right {
    gap: 0;
  }
  
  .user-info {
    display: none;
  }
  
  .user-section {
    padding-left: 0.75rem;
    border-left: none;
    margin-left: 0;
  }
}
</style>
