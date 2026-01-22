<script setup lang="ts">
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const userInfo = useCookie('user_info')
const { success, error: showError } = useToast()

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

const currentUser = decodeUserInfo(userInfo.value)

// Only Admin can access this page
if (!currentUser || currentUser.role !== 'Admin') {
  await navigateTo('/')
}

interface User {
  id: number
  username: string
  email: string
  full_name: string
  department?: string
  role: string
  primary_group_id?: number | null
  is_active: boolean
  created_at?: string
  last_login?: string
}

interface UserGroup {
  id: number
  name: string
  description?: string
}

const users = ref<User[]>([])
const groups = ref<UserGroup[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedUser = ref<User | null>(null)

const form = ref({
  username: '',
  email: '',
  password: '',
  full_name: '',
  department: '',
  role: 'User',
  primary_group_id: null as number | null
})

const roleOptions = [
  { value: 'User', label: 'User' },
  { value: 'Manager', label: 'Manager' },
  { value: 'Admin', label: 'Admin' }
]

const groupOptions = computed(() => [
  { value: null, label: 'None' },
  ...groups.value.map(group => ({ value: group.id, label: group.name }))
])

const getGroupName = (id?: number | null) => {
  if (!id) return '—'
  return groups.value.find(group => group.id === id)?.name || 'Unknown'
}

const ensureAdminPrimaryGroup = () => {
  if (form.value.role === 'Admin' && !form.value.primary_group_id && groups.value.length > 0) {
    form.value.primary_group_id = groups.value[0].id
  }
}

const fetchGroups = async () => {
  try {
    const res = await useApiFetch<UserGroup[]>('/user-groups/')
    groups.value = res as any
    ensureAdminPrimaryGroup()
  } catch (e: any) {
    console.error('Failed to load groups:', e)
  }
}

const fetchUsers = async () => {
  try {
    loading.value = true
    const res = await useApiFetch<User[]>('/users/')
    users.value = res as any
    error.value = null
  } catch (e: any) {
    error.value = 'Failed to load users'
    if (e.response?.status === 401) {
      await navigateTo('/login')
    }
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    username: '',
    email: '',
    password: '',
    full_name: '',
    department: '',
    role: 'User',
    primary_group_id: null
  }
  ensureAdminPrimaryGroup()
}

const openCreateModal = () => {
  resetForm()
  showCreateModal.value = true
}

const openEditModal = (user: User) => {
  selectedUser.value = user
  form.value = {
    username: user.username,
    email: user.email,
    password: '', // Don't populate password
    full_name: user.full_name,
    department: user.department || '',
    role: user.role,
    primary_group_id: user.primary_group_id ?? null
  }
  showEditModal.value = true
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedUser.value = null
  resetForm()
}

const createUser = async () => {
  if (form.value.role === 'Admin' && !form.value.primary_group_id) {
    showError('Admin users must have a primary group')
    return
  }
  try {
    loading.value = true
    await useApiFetch('/auth/register', {
      method: 'POST',
      body: form.value
    })
    await fetchUsers()
    closeModals()
    success('User created successfully!')
  } catch (e: any) {
    showError(e.data?.detail || 'Failed to create user')
  } finally {
    loading.value = false
  }
}

const updateUser = async () => {
  if (!selectedUser.value) return
  if (form.value.role === 'Admin' && !form.value.primary_group_id) {
    showError('Admin users must have a primary group')
    return
  }
  try {
    loading.value = true
    const updateData: any = {
      full_name: form.value.full_name,
      department: form.value.department,
      role: form.value.role,
      primary_group_id: form.value.primary_group_id
    }
    // Only include password if it's not empty
    if (form.value.password) {
      updateData.password = form.value.password
    }

    await useApiFetch(`/users/${selectedUser.value.id}`, {
      method: 'PUT',
      body: updateData
    })
    await fetchUsers()
    closeModals()
    success('User updated successfully!')
  } catch (e: any) {
    showError(e.data?.detail || 'Failed to update user')
  } finally {
    loading.value = false
  }
}

const deleteUser = async (user: User) => {
  if (user.id === currentUser.id) {
    showError('You cannot delete yourself!')
    return
  }

  if (!confirm(`Are you sure you want to delete user "${user.full_name}" (@${user.username})?`)) {
    return
  }

  try {
    loading.value = true
    await useApiFetch(`/users/${user.id}`, { method: 'DELETE' })
    await fetchUsers()
    success('User deleted successfully!')
  } catch (e: any) {
    showError(e.data?.detail || 'Failed to delete user')
  } finally {
    loading.value = false
  }
}

const formatDate = (date: string | undefined) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleString()
}

const tableColumns = [
  { key: 'username', label: 'Username', sortable: true },
  { key: 'full_name', label: 'Full Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
  { key: 'department', label: 'Department', sortable: true },
  { key: 'primary_group_id', label: 'Primary Group', sortable: true },
  { key: 'role', label: 'Role', sortable: true },
  { key: 'last_login', label: 'Last Login', sortable: true },
  { key: 'actions', label: 'Actions', sortable: false }
]

onMounted(() => {
  fetchGroups()
  fetchUsers()
})

watch(() => form.value.role, () => {
  ensureAdminPrimaryGroup()
})
</script>

<template>
  <BaseCard title="User Management" subtitle="Manage user accounts and permissions">
    <template #header>
      <div class="header-actions">
        <BaseButton variant="primary" @click="openCreateModal">
          + Create User
        </BaseButton>
      </div>
    </template>

    <div v-if="loading" class="loading-state">
      <BaseLoadingSpinner size="lg" label="Loading users..." />
    </div>

    <p v-else-if="error" class="error-message">{{ error }}</p>

    <BaseEmptyState
      v-else-if="users.length === 0"
      title="No users found"
      description="Click 'Create User' to add your first user."
      action-text="Create User"
      @action="openCreateModal"
    />

    <BaseTable
      v-else
      :columns="tableColumns"
      :data="users"
      :loading="loading"
      selectable
      sticky-header
      empty-message="No users found"
    >
      <template #cell-username="{ value, row }">
        <div>
          <strong>{{ value }}</strong>
          <BaseBadge v-if="row.id === currentUser.id" variant="info" size="sm" class="ml-2">You</BaseBadge>
        </div>
      </template>

      <template #cell-role="{ value }">
        <BaseBadge
          :variant="value === 'Admin' ? 'danger' : value === 'Manager' ? 'warning' : 'secondary'"
          size="sm"
        >
          {{ value }}
        </BaseBadge>
      </template>

      <template #cell-primary_group_id="{ value }">
        {{ getGroupName(value) }}
      </template>

      <template #cell-department="{ value }">
        {{ value || '—' }}
      </template>

      <template #cell-last_login="{ value }">
        {{ formatDate(value) }}
      </template>

      <template #cell-actions="{ row }">
        <div class="action-buttons">
          <BaseButton
            size="sm"
            variant="secondary"
            @click="openEditModal(row)"
          >
            Edit
          </BaseButton>
          <BaseButton
            v-if="row.id !== currentUser.id"
            size="sm"
            variant="danger"
            @click="deleteUser(row)"
          >
            Delete
          </BaseButton>
        </div>
      </template>
    </BaseTable>

    <!-- Create User Modal -->
    <BaseModal v-model="showCreateModal" title="Create User" size="lg">
      <form @submit.prevent="createUser">
        <BaseInput
          v-model="form.username"
          label="Username"
          placeholder="e.g., jdoe"
          required
          help-text="Unique username for login"
        />

        <BaseInput
          v-model="form.email"
          label="Email"
          type="email"
          placeholder="e.g., john.doe@company.com"
          required
        />

        <BaseInput
          v-model="form.full_name"
          label="Full Name"
          placeholder="e.g., John Doe"
          required
        />

        <BaseInput
          v-model="form.department"
          label="Department"
          placeholder="e.g., Engineering"
        />

        <BaseSelect
          v-model="form.role"
          :options="roleOptions"
          label="Role"
          required
          help-text="User role determines access level"
        />

        <BaseSelect
          v-model="form.primary_group_id"
          :options="groupOptions"
          label="Primary Group"
          :required="form.role === 'Admin'"
          help-text="Required for Admin users"
        />

        <BaseInput
          v-model="form.password"
          label="Password"
          type="password"
          placeholder="Must be at least 8 characters"
          required
          help-text="Must contain uppercase, lowercase, number, and special character"
        />
      </form>

      <template #footer>
        <BaseButton variant="secondary" :disabled="loading" @click="closeModals">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" :loading="loading" @click="createUser">
          Create User
        </BaseButton>
      </template>
    </BaseModal>

    <!-- Edit User Modal -->
    <BaseModal v-model="showEditModal" title="Edit User" size="lg">
      <form @submit.prevent="updateUser">
        <BaseInput
          v-model="form.username"
          label="Username"
          disabled
          help-text="Username cannot be changed"
        />

        <BaseInput
          v-model="form.email"
          label="Email"
          disabled
          help-text="Email cannot be changed"
        />

        <BaseInput
          v-model="form.full_name"
          label="Full Name"
          required
        />

        <BaseInput
          v-model="form.department"
          label="Department"
        />

        <BaseSelect
          v-model="form.role"
          :options="roleOptions"
          label="Role"
          required
          :disabled="selectedUser?.id === currentUser.id"
          :help-text="selectedUser?.id === currentUser.id ? 'You cannot change your own role' : ''"
        />

        <BaseSelect
          v-model="form.primary_group_id"
          :options="groupOptions"
          label="Primary Group"
          :required="form.role === 'Admin'"
          help-text="Required for Admin users"
        />

        <BaseInput
          v-model="form.password"
          label="New Password (Optional)"
          type="password"
          placeholder="Leave empty to keep current password"
          help-text="Must contain uppercase, lowercase, number, and special character"
        />
      </form>

      <template #footer>
        <BaseButton variant="secondary" :disabled="loading" @click="closeModals">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" :loading="loading" @click="updateUser">
          Save Changes
        </BaseButton>
      </template>
    </BaseModal>
  </BaseCard>
</template>

<style scoped>
.header-actions {
  display: flex;
  justify-content: flex-end;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: var(--spacing-12);
}

.error-message {
  color: var(--color-error);
  padding: var(--spacing-4);
  text-align: center;
}

.action-buttons {
  display: flex;
  gap: var(--spacing-2);
}

.ml-2 {
  margin-left: var(--spacing-2);
}
</style>
