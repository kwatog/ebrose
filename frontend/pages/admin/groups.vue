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

if (!currentUser || !['Manager', 'Admin'].includes(currentUser.role)) {
  await navigateTo('/')
}

interface UserGroup {
  id: number
  name: string
  description: string
  created_by?: number
  created_at?: string
}

interface User {
  id: number
  username: string
  full_name: string
  department: string
  role: string
}

interface GroupMembership {
  id: number
  user_id: number
  group_id: number
  added_by?: number
  added_at?: string
}

const groups = ref<UserGroup[]>([])
const users = ref<User[]>([])
const selectedGroup = ref<UserGroup | null>(null)
const groupMembers = ref<GroupMembership[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const showCreateGroupModal = ref(false)
const showAddMemberModal = ref(false)
const newGroup = ref({
  name: '',
  description: ''
})
const selectedUserId = ref<number | null>(null)

const userOptions = computed(() => {
  const memberUserIds = groupMembers.value.map(m => m.user_id)
  return users.value
    .filter(u => !memberUserIds.includes(u.id))
    .map(u => ({ 
      value: u.id, 
      label: `${u.full_name} (@${u.username}) - ${u.role}` 
    }))
})

const fetchGroups = async () => {
  try {
    const res = await useApiFetch<UserGroup[]>(`/user-groups`)
    groups.value = res
  } catch (e: any) {
    error.value = 'Failed to load groups'
    if (e.response?.status === 401) await navigateTo('/login')
  }
}

const fetchUsers = async () => {
  try {
    const res = await useApiFetch<User[]>(`/users`)
    users.value = res
  } catch (e: any) {
    console.error('Failed to load users:', e)
  }
}

const fetchGroupMembers = async (groupId: number) => {
  try {
    const res = await useApiFetch<GroupMembership[]>(`/user-groups/${groupId}/members`)
    groupMembers.value = res
  } catch (e: any) {
    error.value = 'Failed to load group members'
  }
}

const createGroup = async () => {
  try {
    await useApiFetch(`/user-groups`, { method: 'POST', body: newGroup.value })
    newGroup.value = { name: '', description: '' }
    showCreateGroupModal.value = false
    await fetchGroups()
    success('Group created successfully!')
  } catch (e: any) {
    showError(e.data?.detail || 'Failed to create group')
  }
}

const addMemberToGroup = async () => {
  if (!selectedGroup.value || !selectedUserId.value) return
  try {
    await useApiFetch(`/user-groups/${selectedGroup.value.id}/members`, {
      method: 'POST',
      body: {
        user_id: selectedUserId.value,
        group_id: selectedGroup.value.id
      }
    })
    selectedUserId.value = null
    showAddMemberModal.value = false
    await fetchGroupMembers(selectedGroup.value.id)
    success('Member added successfully!')
  } catch (e: any) {
    showError(e.data?.detail || 'Failed to add member')
  }
}

const removeMemberFromGroup = async (userId: number) => {
  if (!selectedGroup.value) return
  try {
    await useApiFetch(`/user-groups/${selectedGroup.value.id}/members/${userId}`, { method: 'DELETE' })
    await fetchGroupMembers(selectedGroup.value.id)
    success('Member removed successfully!')
  } catch (e: any) {
    showError(e.data?.detail || 'Failed to remove member')
  }
}

const selectGroup = async (group: UserGroup) => {
  selectedGroup.value = group
  await fetchGroupMembers(group.id)
}

const getUserById = (userId: number) => {
  return users.value.find(u => u.id === userId)
}

onMounted(async () => {
  await Promise.all([fetchGroups(), fetchUsers()])
  loading.value = false
})
</script>

<template>
  <div>
    <BaseCard title="User Groups Management" subtitle="Manage user groups and memberships">
      <template #header>
        <div class="header-actions">
          <BaseButton variant="primary" @click="showCreateGroupModal = true">
            Create New Group
          </BaseButton>
        </div>
      </template>

      <div v-if="loading" class="loading-state">
        <LoadingSpinner size="lg" label="Loading groups..." />
      </div>

      <p v-else-if="error" class="error-message">{{ error }}</p>

      <div v-else class="groups-layout">
        <BaseCard title="Groups" :subtitle="`${groups.length} groups`" padding="md">
          <EmptyState
            v-if="groups.length === 0"
            title="No groups found"
            description="Create your first group to get started."
            action-text="Create Group"
            @action="showCreateGroupModal = true"
          />

          <div v-else class="groups-list">
            <div 
              v-for="group in groups" 
              :key="group.id"
              class="group-item"
              :class="{ active: selectedGroup?.id === group.id }"
              @click="selectGroup(group)"
            >
              <div class="group-name">{{ group.name }}</div>
              <div class="group-desc">{{ group.description || 'No description' }}</div>
            </div>
          </div>
        </BaseCard>

        <BaseCard v-if="selectedGroup" :title="`${selectedGroup.name} Members`" padding="md">
          <template #header>
            <div class="panel-header">
              <BaseButton size="sm" variant="primary" @click="showAddMemberModal = true">
                Add Member
              </BaseButton>
            </div>
          </template>

          <EmptyState
            v-if="groupMembers.length === 0"
            title="No members"
            description="Add members to this group."
          />

          <div v-else class="members-list">
            <div 
              v-for="membership in groupMembers" 
              :key="membership.id"
              class="member-item"
            >
              <div class="member-info">
                <div class="member-name">
                  {{ getUserById(membership.user_id)?.full_name || 'Unknown User' }}
                </div>
                <div class="member-details">
                  @{{ getUserById(membership.user_id)?.username }} - 
                  {{ getUserById(membership.user_id)?.role }}
                </div>
              </div>
              <BaseButton
                size="sm"
                variant="danger"
                @click="removeMemberFromGroup(membership.user_id)"
              >
                Remove
              </BaseButton>
            </div>
          </div>
        </BaseCard>

        <BaseCard v-else padding="lg">
          <EmptyState
            title="Select a Group"
            description="Choose a group from the left to view and manage its members."
          />
        </BaseCard>
      </div>
    </BaseCard>

    <BaseModal v-model="showCreateGroupModal" title="Create New Group" size="md">
      <form @submit.prevent="createGroup">
        <BaseInput
          v-model="newGroup.name"
          label="Group Name"
          placeholder="e.g., Engineering Team"
          required
        />

        <BaseTextarea
          v-model="newGroup.description"
          label="Description"
          placeholder="Optional description"
          rows="3"
        />
      </form>

      <template #footer>
        <BaseButton variant="secondary" @click="showCreateGroupModal = false">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" @click="createGroup">
          Create Group
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal v-model="showAddMemberModal" :title="`Add Member to ${selectedGroup?.name}`" size="md">
      <form @submit.prevent="addMemberToGroup">
        <BaseSelect
          v-model="selectedUserId"
          :options="userOptions"
          label="Select User"
          placeholder="Choose a user..."
          required
        />
      </form>

      <template #footer>
        <BaseButton variant="secondary" @click="showAddMemberModal = false">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" @click="addMemberToGroup" :disabled="!selectedUserId">
          Add Member
        </BaseButton>
      </template>
    </BaseModal>
  </div>
</template>

<style scoped>
.header-actions {
  display: flex;
  justify-content: flex-end;
}

.groups-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-6);
  min-height: 400px;
}

.panel-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.groups-list, .members-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.group-item {
  padding: var(--spacing-4);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.group-item:hover {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.05);
}

.group-item.active {
  border-color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.1);
}

.group-name, .member-name {
  font-weight: 600;
  margin-bottom: var(--spacing-1);
}

.group-desc, .member-details {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
}

.member-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-3);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-md);
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

@media (max-width: 900px) {
  .groups-layout {
    grid-template-columns: 1fr;
  }
}
</style>
