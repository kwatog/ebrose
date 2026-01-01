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
</script>

<template>
  <div>
    <header class="header" v-if="$route.path !== '/login'">
      <div>
        <div class="header-title">Ebrose</div>
        <div class="header-sub">Chamber of Spend Records</div>
      </div>
      <div class="flex items-center gap-4">
        <nav style="display: flex; align-items: center; gap: 1rem;">
          <NuxtLink to="/">Dashboard</NuxtLink>
          <NuxtLink to="/budget-items">Budget Items</NuxtLink>
          <NuxtLink to="/business-cases">Business Cases</NuxtLink>
          <NuxtLink to="/line-items">Line Items</NuxtLink>
          <NuxtLink to="/wbs">WBS</NuxtLink>
          <NuxtLink to="/assets">Assets</NuxtLink>
          <NuxtLink to="/purchase-orders">Purchase Orders</NuxtLink>
          <NuxtLink to="/goods-receipts">Goods Receipts</NuxtLink>
          <NuxtLink to="/resources">Resources</NuxtLink>
          <NuxtLink to="/allocations">Allocations</NuxtLink>

          <template v-if="isAdminOrManager">
            <NuxtLink to="/admin/groups">Groups</NuxtLink>
            <NuxtLink to="/admin/audit">Audit Logs</NuxtLink>
          </template>
        </nav>
        <div v-if="user" class="user-menu" style="display: flex; align-items: center; gap: 1rem; margin-left: 1rem; padding-left: 1rem; border-left: 1px solid #eee;">
          <span style="font-size: 0.9rem; color: #666;">{{ user.username }} ({{ user.role }})</span>
          <button @click="logout" class="btn-text" style="background:none; border:none; cursor:pointer; color: #cc0000; font-weight:600;">Logout</button>
        </div>
      </div>
    </header>
    <main class="main-container">
      <slot />
    </main>
  </div>
</template>
