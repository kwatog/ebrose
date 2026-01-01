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

interface BudgetItem {
  id: number
  workday_ref: string
  title: string
  description?: string
  budget_amount: string
  currency: string
  fiscal_year: number
  owner_group_id: number
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

const items = ref<BudgetItem[]>([])
const groups = ref<UserGroup[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const filterFiscalYear = ref<number | null>(null)
const filterOwnerGroup = ref<number | null>(null)

const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectedItem = ref<BudgetItem | null>(null)

const form = ref({
  workday_ref: '',
  title: '',
  description: '',
  budget_amount: '',
  currency: 'USD',
  fiscal_year: new Date().getFullYear(),
  owner_group_id: 0
})

const currencyOptions = [
  { value: 'USD', label: 'USD' },
  { value: 'EUR', label: 'EUR' },
  { value: 'GBP', label: 'GBP' }
]

const fiscalYearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 7 }, (_, i) => ({
    value: currentYear + i - 1,
    label: String(currentYear + i - 1)
  }))
})

const groupOptions = computed(() => 
  groups.value.map(g => ({ value: g.id, label: g.name }))
)

const fetchGroups = async () => {
  try {
    const res = await useApiFetch<UserGroup[]>('/user-groups')
    groups.value = res as any
    if (groups.value.length > 0 && form.value.owner_group_id === 0) {
      form.value.owner_group_id = groups.value[0].id
    }
  } catch (e: any) {
    console.error('Failed to load groups:', e)
  }
}

const fetchItems = async () => {
  try {
    loading.value = true
    let url = '/budget-items?limit=100'
    if (filterFiscalYear.value) {
      url += `&fiscal_year=${filterFiscalYear.value}`
    }
    if (filterOwnerGroup.value) {
      url += `&owner_group_id=${filterOwnerGroup.value}`
    }
    const res = await useApiFetch<BudgetItem[]>(url)
    items.value = res as any
    error.value = null
  } catch (e: any) {
    console.error(e)
    error.value = 'Failed to load budget items.'
    if (e.response?.status === 401) {
      navigateTo('/login')
    }
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.value = {
    workday_ref: '',
    title: '',
    description: '',
    budget_amount: '',
    currency: 'USD',
    fiscal_year: new Date().getFullYear(),
    owner_group_id: groups.value[0]?.id || 0
  }
}

const openCreateModal = () => {
  resetForm()
  showCreateModal.value = true
}

const openEditModal = (item: BudgetItem) => {
  selectedItem.value = item
  form.value = {
    workday_ref: item.workday_ref,
    title: item.title,
    description: item.description || '',
    budget_amount: item.budget_amount,
    currency: item.currency,
    fiscal_year: item.fiscal_year,
    owner_group_id: item.owner_group_id
  }
  showEditModal.value = true
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  selectedItem.value = null
  resetForm()
}

const createItem = async () => {
  try {
    loading.value = true
    await useApiFetch('/budget-items', {
      method: 'POST',
      body: form.value
    })
    await fetchItems()
    closeModals()
    success('Budget item created successfully!')
  } catch (e: any) {
    showError(`Failed to create budget item: ${e.data?.detail || e.message}`)
  } finally {
    loading.value = false
  }
}

const updateItem = async () => {
  if (!selectedItem.value) return
  try {
    loading.value = true
    await useApiFetch(`/budget-items/${selectedItem.value.id}`, {
      method: 'PUT',
      body: {
        title: form.value.title,
        description: form.value.description,
        budget_amount: form.value.budget_amount,
        currency: form.value.currency,
        fiscal_year: form.value.fiscal_year
      }
    })
    await fetchItems()
    closeModals()
    success('Budget item updated successfully!')
  } catch (e: any) {
    showError(`Failed to update budget item: ${e.data?.detail || e.message}`)
  } finally {
    loading.value = false
  }
}

const deleteItem = async (item: BudgetItem) => {
  if (!confirm(`Are you sure you want to delete budget item "${item.title}"?`)) {
    return
  }
  try {
    loading.value = true
    await useApiFetch(`/budget-items/${item.id}`, {
      method: 'DELETE'
    })
    await fetchItems()
    success('Budget item deleted successfully!')
  } catch (e: any) {
    showError(`Failed to delete budget item: ${e.data?.detail || e.message}`)
  } finally {
    loading.value = false
  }
}

const canEdit = (item: BudgetItem) => {
  if (!currentUser) return false
  if (['Admin', 'Manager'].includes(currentUser.role)) return true
  return item.created_by === currentUser.id
}

const canDelete = () => {
  return currentUser && ['Admin', 'Manager'].includes(currentUser.role)
}

const formatCurrency = (amount: string | number, currency: string) => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(num)
}

const tableColumns = [
  { key: 'workday_ref', label: 'Workday Ref', sortable: true },
  { key: 'title', label: 'Title', sortable: true },
  { key: 'budget_amount', label: 'Budget Amount', sortable: true, align: 'right' as const },
  { key: 'fiscal_year', label: 'Fiscal Year', sortable: true, align: 'center' as const },
  { key: 'owner_group', label: 'Owner Group', sortable: false },
  { key: 'actions', label: 'Actions', sortable: false }
]

const getGroupName = (id: number) => groups.value.find(g => g.id === id)?.name || 'Unknown'

onMounted(async () => {
  await fetchGroups()
  await fetchItems()
})
</script>

<template>
  <BaseCard title="Budget Items" subtitle="Manage budget allocations from Workday">
    <template #header>
      <div class="header-actions">
        <BaseButton variant="primary" @click="openCreateModal">
          + Create Budget Item
        </BaseButton>
      </div>
    </template>

    <div class="filters">
      <BaseSelect
        v-model="filterFiscalYear"
        :options="[{ value: null, label: 'All Years' }, ...fiscalYearOptions]"
        label="Fiscal Year"
        @change="fetchItems"
      />
      <BaseSelect
        v-model="filterOwnerGroup"
        :options="[{ value: null, label: 'All Groups' }, ...groupOptions]"
        label="Owner Group"
        @change="fetchItems"
      />
    </div>

    <div v-if="loading" class="loading-state">
      <LoadingSpinner size="lg" label="Loading budget items..." />
    </div>

    <p v-else-if="error" class="error-message">{{ error }}</p>

    <EmptyState
      v-else-if="items.length === 0"
      title="No budget items found"
      description="Click 'Create Budget Item' to add your first budget."
      action-text="Create Budget Item"
      @action="openCreateModal"
    />

    <BaseTable
      v-else
      :columns="tableColumns"
      :data="items"
      :loading="loading"
      selectable
      sticky-header
      empty-message="No budget items found"
      @row-click="openEditModal"
    >
      <template #cell-workday_ref="{ value }">
        <code class="ref-code">{{ value }}</code>
      </template>

      <template #cell-title="{ row, value }">
        <div>
          <strong>{{ value }}</strong>
          <div v-if="row.description" class="description">{{ row.description }}</div>
        </div>
      </template>

      <template #cell-budget_amount="{ value, row }">
        {{ formatCurrency(value, row.currency) }}
      </template>

      <template #cell-fiscal_year="{ value }">
        <BaseBadge variant="secondary" size="sm">{{ value }}</BaseBadge>
      </template>

      <template #cell-owner_group="{ row }">
        <BaseBadge variant="primary" size="sm">{{ getGroupName(row.owner_group_id) }}</BaseBadge>
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
            @click="deleteItem(row)"
          >
            Delete
          </BaseButton>
        </div>
      </template>
    </BaseTable>

    <BaseModal v-model="showCreateModal" title="Create Budget Item" size="lg">
      <form @submit.prevent="createItem">
        <BaseInput
          v-model="form.workday_ref"
          label="Workday Reference"
          placeholder="e.g., WD-2025-FIN-001"
          required
        />

        <BaseInput
          v-model="form.title"
          label="Title"
          placeholder="e.g., Cloud Infrastructure Budget 2025"
          required
        />

        <BaseTextarea
          v-model="form.description"
          label="Description"
          placeholder="Optional description"
          rows="3"
        />

        <div class="form-row">
          <BaseInput
            v-model="form.budget_amount"
            label="Budget Amount"
            placeholder="0.00"
            required
          />
          <BaseSelect
            v-model="form.currency"
            :options="currencyOptions"
            label="Currency"
            required
          />
        </div>

        <div class="form-row">
          <BaseInput
            v-model.number="form.fiscal_year"
            label="Fiscal Year"
            type="number"
            required
          />
          <BaseSelect
            v-model="form.owner_group_id"
            :options="groupOptions"
            label="Owner Group"
            required
          />
        </div>
      </form>

      <template #footer>
        <BaseButton variant="secondary" :disabled="loading" @click="closeModals">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" :loading="loading" @click="createItem">
          Create Budget Item
        </BaseButton>
      </template>
    </BaseModal>

    <BaseModal v-model="showEditModal" title="Edit Budget Item" size="lg">
      <form @submit.prevent="updateItem">
        <BaseInput
          v-model="form.workday_ref"
          label="Workday Reference"
          disabled
          help-text="Workday reference cannot be changed"
        />

        <BaseInput
          v-model="form.title"
          label="Title"
          required
        />

        <BaseTextarea
          v-model="form.description"
          label="Description"
          rows="3"
        />

        <div class="form-row">
          <BaseInput
            v-model="form.budget_amount"
            label="Budget Amount"
            required
          />
          <BaseSelect
            v-model="form.currency"
            :options="currencyOptions"
            label="Currency"
            required
          />
        </div>

        <BaseInput
          v-model.number="form.fiscal_year"
          label="Fiscal Year"
          type="number"
          required
        />
      </form>

      <template #footer>
        <BaseButton variant="secondary" :disabled="loading" @click="closeModals">
          Cancel
        </BaseButton>
        <BaseButton variant="primary" :loading="loading" @click="updateItem">
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

.ref-code {
  font-family: monospace;
  background: var(--color-gray-100);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
}

.description {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
  margin-top: var(--spacing-1);
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
