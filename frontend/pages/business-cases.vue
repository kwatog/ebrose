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

interface BusinessCase {
  id: number
  title: string
  description?: string
  requestor?: string
  dept?: string
  lead_group_id?: number
  estimated_cost?: string
  status?: string
  created_by?: number
  updated_by?: number
  created_at?: string
  updated_at?: string
}

interface UserGroup {
  id: number
  name: string
  description?: string
}

const cases = ref<BusinessCase[]>([])
const groups = ref<UserGroup[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const filterStatus = ref<string | null>(null)
const filterRequestor = ref<string>('')

const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedCase = ref<BusinessCase | null>(null)

const form = ref({
  title: '',
  description: '',
  requestor: '',
  dept: '',
  lead_group_id: null as number | null,
  estimated_cost: '',
  status: 'Draft'
})

const statuses = ['Draft', 'Submitted', 'Under Review', 'Approved', 'Rejected', 'Completed']

const groupOptions = computed(() => 
  groups.value.map(g => ({ value: g.id, label: g.name }))
)

const statusOptions = computed(() => 
  statuses.map(s => ({ value: s, label: s }))
)

const filterStatusOptions = computed(() => [
  { value: null, label: 'All Statuses' },
  ...statusOptions.value
])

const fetchGroups = async () => {
  try {
    const res = await useApiFetch<UserGroup[]>('/user-groups')
    groups.value = res as any
  } catch (e: any) {
    console.error('Failed to load groups:', e)
  }
}

const fetchCases = async () => {
  try {
    loading.value = true
    let url = '/business-cases?limit=100'
    if (filterStatus.value) {
      url += `&status=${filterStatus.value}`
    }
    if (filterRequestor.value) {
      url += `&requestor=${filterRequestor.value}`
    }
    const res = await useApiFetch<BusinessCase[]>(url)
    cases.value = res as any
    error.value = null
  } catch (e: any) {
    console.error(e)
    error.value = 'Failed to load business cases.'
    if (e.response?.status === 401) {
      navigateTo('/login')
    }
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    requestor: currentUser?.full_name || '',
    dept: currentUser?.department || '',
    lead_group_id: null,
    estimated_cost: '',
    status: 'Draft'
  }
}

const openCreateModal = () => {
  resetForm()
  showCreateModal.value = true
}

const openEditModal = (bc: BusinessCase) => {
  selectedCase.value = bc
  form.value = {
    title: bc.title || '',
    description: bc.description || '',
    requestor: bc.requestor || '',
    dept: bc.dept || '',
    lead_group_id: bc.lead_group_id || null,
    estimated_cost: bc.estimated_cost ? String(bc.estimated_cost) : '',
    status: bc.status || 'Draft'
  }
  showEditModal.value = true
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedCase.value = null
  resetForm()
}

const createCase = async () => {
  try {
    loading.value = true
    await useApiFetch('/business-cases', {
      method: 'POST',
      body: form.value
    })
    await fetchCases()
    closeModals()
    success('Business case created successfully!')
  } catch (e: any) {
    showError(`Failed to create business case: ${e.data?.detail || e.message}`)
  } finally {
    loading.value = false
  }
}

const updateCase = async () => {
  if (!selectedCase.value) return
  try {
    loading.value = true
    await useApiFetch(`/business-cases/${selectedCase.value.id}`, {
      method: 'PUT',
      body: form.value
    })
    await fetchCases()
    closeModals()
    success('Business case updated successfully!')
  } catch (e: any) {
    showError(`Failed to update business case: ${e.data?.detail || e.message}`)
  } finally {
    loading.value = false
  }
}

const deleteCase = async (bc: BusinessCase) => {
  if (!confirm(`Are you sure you want to delete business case "${bc.title}"?`)) {
    return
  }
  try {
    loading.value = true
    await useApiFetch(`/business-cases/${bc.id}`, {
      method: 'DELETE'
    })
    await fetchCases()
    success('Business case deleted successfully!')
  } catch (e: any) {
    showError(`Failed to delete business case: ${e.data?.detail || e.message}`)
  } finally {
    loading.value = false
  }
}

const canEdit = (bc: BusinessCase) => {
  if (!currentUser) return false
  if (['Admin', 'Manager'].includes(currentUser.role)) return true
  return bc.created_by === currentUser.id
}

const canDelete = () => {
  return currentUser && ['Admin', 'Manager'].includes(currentUser.role)
}

const getStatusColor = (status?: string) => {
  const colors: Record<string, 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info'> = {
    'Draft': 'secondary',
    'Submitted': 'info',
    'Under Review': 'warning',
    'Approved': 'success',
    'Rejected': 'danger',
    'Completed': 'primary'
  }
  return colors[status || 'Draft'] || 'secondary'
}

const getGroupName = (id?: number) => groups.value.find(g => g.id === id)?.name || '-'

const formatCurrency = (amount?: string) => {
  if (!amount) return '-'
  const num = parseFloat(amount)
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(num)
}

const tableColumns = [
  { key: 'title', label: 'Title', sortable: true },
  { key: 'requestor', label: 'Requestor', sortable: true },
  { key: 'dept', label: 'Department', sortable: false },
  { key: 'lead_group', label: 'Lead Group', sortable: false },
  { key: 'estimated_cost', label: 'Estimated Cost', sortable: true, align: 'right' as const },
  { key: 'status', label: 'Status', sortable: true },
  { key: 'actions', label: 'Actions', sortable: false }
]

onMounted(async () => {
  await fetchGroups()
  await fetchCases()
})
</script>

<template>
  <BaseCard title="Business Cases" subtitle="Track business case requests and approvals">
    <template #header>
      <div class="header-actions">
        <BaseButton variant="primary" @click="openCreateModal">
          + Create Business Case
        </BaseButton>
      </div>
    </template>

    <div class="filters">
      <BaseSelect
        v-model="filterStatus"
        :options="filterStatusOptions"
        label="Status"
        @change="fetchCases"
      />
      <BaseInput
        v-model="filterRequestor"
        label="Requestor"
        placeholder="Filter by name..."
        @input="fetchCases"
      />
    </div>

    <div v-if="loading" class="loading-state">
      <LoadingSpinner size="lg" label="Loading business cases..." />
    </div>

    <p v-else-if="error" class="error-message">{{ error }}</p>

    <EmptyState
      v-else-if="cases.length === 0"
      title="No business cases found"
      description="Click 'Create Business Case' to add your first business case."
      action-text="Create Business Case"
      @action="openCreateModal"
    />

    <BaseTable
      v-else
      :columns="tableColumns"
      :data="cases"
      :loading="loading"
      selectable
      sticky-header
      empty-message="No business cases found"
      @row-click="openEditModal"
    >
      <template #cell-title="{ row, value }">
        <div>
          <strong>{{ value }}</strong>
          <div v-if="row.description" class="description">{{ row.description }}</div>
        </div>
      </template>

      <template #cell-lead_group="{ row }">
        <BaseBadge variant="primary" size="sm">{{ getGroupName(row.lead_group_id) }}</BaseBadge>
      </template>

      <template #cell-estimated_cost="{ value }">
        <span class="amount">{{ formatCurrency(value) }}</span>
      </template>

      <template #cell-status="{ value }">
        <BaseBadge :variant="getStatusColor(value)" size="sm">{{ value || 'Draft' }}</BaseBadge>
      </template>

      <template #cell-actions="{ row }">
        <div class="action-buttons" v-if="canEdit(row) || canDelete()">
          <BaseButton
            v-if="canEdit(row)"
            size="sm"
            variant="secondary"
            @click="openEditModal(row)"
          >
            Edit
          </BaseButton>
          <BaseButton
            v-if="canDelete()"
            size="sm"
            variant="danger"
            @click="deleteCase(row)"
          >
            Delete
          </BaseButton>
        </div>
      </template>
    </BaseTable>

    <BaseModal v-model="showCreateModal" title="Create Business Case" size="lg">
      <form @submit.prevent="createCase">
        <BaseInput
          v-model="form.title"
          label="Title"
          placeholder="e.g., Cloud Migration Project"
          required
        />

        <BaseTextarea
          v-model="form.description"
          label="Description"
          placeholder="Detailed description of the business case..."
          rows="4"
        />

        <div class="form-row">
          <BaseInput
            v-model="form.requestor"
            label="Requestor"
            placeholder="Name"
            required
          />
          <BaseInput
            v-model="form.dept"
            label="Department"
            placeholder="Department"
            required
          />
        </div>

        <BaseSelect
          v-model="form.lead_group_id"
          :options="groupOptions"
          label="Lead Group"
        />

        <div class="form-row">
          <BaseInput
            v-model="form.estimated_cost"
            label="Estimated Cost (USD)"
            placeholder="0.00"
            type="text"
          />
          <BaseSelect
            v-model="form.status"
            :options="statusOptions"
            label="Status"
            required
          />
        </div>
      </form>

      <template #footer>
        <BaseButton variant="secondary" :disabled="loading" @click="closeModals">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" :loading="loading" @click="createCase">
          Create Business Case
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal v-model="showEditModal" title="Edit Business Case" size="lg">
      <form @submit.prevent="updateCase">
        <BaseInput
          v-model="form.title"
          label="Title"
          required
        />

        <BaseTextarea
          v-model="form.description"
          label="Description"
          rows="4"
        />

        <div class="form-row">
          <BaseInput
            v-model="form.requestor"
            label="Requestor"
            required
          />
          <BaseInput
            v-model="form.dept"
            label="Department"
            required
          />
        </div>

        <BaseSelect
          v-model="form.lead_group_id"
          :options="groupOptions"
          label="Lead Group"
        />

        <div class="form-row">
          <BaseInput
            v-model="form.estimated_cost"
            label="Estimated Cost (USD)"
            type="text"
          />
          <BaseSelect
            v-model="form.status"
            :options="statusOptions"
            label="Status"
            required
          />
        </div>
      </form>

      <template #footer>
        <BaseButton variant="secondary" :disabled="loading" @click="closeModals">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" :loading="loading" @click="updateCase">
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

.filters {
  display: flex;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-4);
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
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

.description {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
  margin-top: var(--spacing-1);
  max-width: 400px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.amount {
  font-weight: 600;
  color: var(--color-success);
}

.action-buttons {
  display: flex;
  gap: var(--spacing-2);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-4);
}

@media (max-width: 640px) {
  .filters {
    flex-direction: column;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
