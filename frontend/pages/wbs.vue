<script setup lang="ts">

interface WBS {
  id: number
  business_case_line_item_id: number
  wbs_code: string
  description?: string
  owner_group_id: number
  status?: string
  created_by?: number
  updated_by?: number
  created_at?: string
  updated_at?: string
}

interface LineItem {
  id: number
  business_case_id: number
  budget_item_id: number
  title: string
  spend_category: string
}

interface Group {
  id: number
  name: string
}

const userCookie = useCookie('user_info')
const user = computed(() => userCookie.value)

const items = ref<WBS[]>([])
const lineItems = ref<LineItem[]>([])
const groups = ref<Group[]>([])

const showCreateModal = ref(false)
const showEditModal = ref(false)

const form = ref({
  business_case_line_item_id: 0,
  wbs_code: '',
  description: '',
  owner_group_id: 0,
  status: 'Active'
})

const editingItem = ref<WBS | null>(null)

// Filters
const filterStatus = ref('')
const filterLineItem = ref(0)

const statuses = ['Active', 'Inactive', 'Closed']

// Fetch data
const fetchItems = async () => {
  try {
    const data = await useApiFetch('/wbs', { method: 'GET' })
    items.value = data as WBS[]
  } catch (e: any) {
    alert(`Failed to fetch WBS items: ${e.data?.detail || e.message}`)
  }
}

const fetchLineItems = async () => {
  try {
    const data = await useApiFetch('/business-case-line-items', { method: 'GET' })
    lineItems.value = data as LineItem[]
  } catch (e: any) {
    console.error('Failed to fetch line items:', e)
  }
}

const fetchGroups = async () => {
  try {
    const data = await useApiFetch('/groups', { method: 'GET' })
    groups.value = data as Group[]
  } catch (e: any) {
    console.error('Failed to fetch groups:', e)
  }
}

onMounted(() => {
  fetchItems()
  fetchLineItems()
  fetchGroups()
})

// Computed
const filteredItems = computed(() => {
  let result = items.value
  if (filterStatus.value) {
    result = result.filter(item => item.status === filterStatus.value)
  }
  if (filterLineItem.value) {
    result = result.filter(item => item.business_case_line_item_id === filterLineItem.value)
  }
  return result
})

// Helpers
const getLineItemTitle = (id: number) => {
  return lineItems.value.find(li => li.id === id)?.title || 'Unknown'
}

const getGroupName = (id: number) => {
  return groups.value.find(g => g.id === id)?.name || 'Unknown'
}

const getStatusColor = (status?: string) => {
  const colors: Record<string, string> = {
    'Active': '#10b981',
    'Inactive': '#6b7280',
    'Closed': '#ef4444'
  }
  return colors[status || 'Active'] || '#6b7280'
}

// Permissions
const canEdit = (item: WBS) => {
  if (!user.value) return false
  if (user.value.role === 'Admin') return true
  if (user.value.role === 'Manager') return true
  return item.created_by === user.value.id
}

const canDelete = (item: WBS) => {
  if (!user.value) return false
  if (user.value.role === 'Admin') return true
  if (user.value.role === 'Manager') return true
  return false
}

// CRUD operations
const openCreateModal = () => {
  form.value = {
    business_case_line_item_id: 0,
    wbs_code: '',
    description: '',
    owner_group_id: 0,
    status: 'Active'
  }
  showCreateModal.value = true
}

const openEditModal = (item: WBS) => {
  editingItem.value = item
  form.value = {
    business_case_line_item_id: item.business_case_line_item_id,
    wbs_code: item.wbs_code,
    description: item.description || '',
    owner_group_id: item.owner_group_id,
    status: item.status || 'Active'
  }
  showEditModal.value = true
}

const closeModals = () => {
  showCreateModal.value = false
  showEditModal.value = false
  editingItem.value = null
}

const createItem = async () => {
  try {
    if (!form.value.business_case_line_item_id) {
      alert('Please select a line item')
      return
    }
    if (!form.value.wbs_code.trim()) {
      alert('WBS Code is required')
      return
    }

    await useApiFetch('/wbs', {
      method: 'POST',
      body: form.value
    })
    await fetchItems()
    closeModals()
  } catch (e: any) {
    alert(`Failed to create WBS: ${e.data?.detail || e.message}`)
  }
}

const updateItem = async () => {
  if (!editingItem.value) return
  try {
    await useApiFetch(`/wbs/${editingItem.value.id}`, {
      method: 'PUT',
      body: {
        wbs_code: form.value.wbs_code,
        description: form.value.description,
        status: form.value.status
      }
    })
    await fetchItems()
    closeModals()
  } catch (e: any) {
    alert(`Failed to update WBS: ${e.data?.detail || e.message}`)
  }
}

const deleteItem = async (item: WBS) => {
  if (!confirm(`Are you sure you want to delete WBS "${item.wbs_code}"?`)) return
  try {
    await useApiFetch(`/wbs/${item.id}`, { method: 'DELETE' })
    await fetchItems()
  } catch (e: any) {
    alert(`Failed to delete WBS: ${e.data?.detail || e.message}`)
  }
}
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Work Breakdown Structure (WBS)</h1>
      <button @click="openCreateModal" class="btn-primary">+ Create WBS</button>
    </div>

    <!-- Filters -->
    <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
      <div style="flex: 1; min-width: 200px;">
        <label style="display: block; margin-bottom: 0.25rem; font-size: 0.9rem; color: #666;">Status</label>
        <select v-model="filterStatus" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
          <option value="">All Statuses</option>
          <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
        </select>
      </div>
      <div style="flex: 1; min-width: 200px;">
        <label style="display: block; margin-bottom: 0.25rem; font-size: 0.9rem; color: #666;">Line Item</label>
        <select v-model.number="filterLineItem" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
          <option :value="0">All Line Items</option>
          <option v-for="li in lineItems" :key="li.id" :value="li.id">{{ li.title }}</option>
        </select>
      </div>
    </div>

    <!-- List -->
    <div v-if="filteredItems.length === 0" class="empty-state">
      <p>No WBS items found</p>
      <button @click="openCreateModal" class="btn-primary">Create First WBS</button>
    </div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>WBS Code</th>
            <th>Line Item</th>
            <th>Description</th>
            <th>Owner Group</th>
            <th>Status</th>
            <th>Created By</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td><strong>{{ item.wbs_code }}</strong></td>
            <td>{{ getLineItemTitle(item.business_case_line_item_id) }}</td>
            <td>{{ item.description || '-' }}</td>
            <td>{{ getGroupName(item.owner_group_id) }}</td>
            <td>
              <span class="badge" :style="{ backgroundColor: getStatusColor(item.status) }">
                {{ item.status || 'Active' }}
              </span>
            </td>
            <td>User #{{ item.created_by }}</td>
            <td>
              <div style="display: flex; gap: 0.5rem;">
                <button v-if="canEdit(item)" @click="openEditModal(item)" class="btn-sm">Edit</button>
                <button v-if="canDelete(item)" @click="deleteItem(item)" class="btn-sm btn-danger">Delete</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create WBS</h2>
          <button @click="closeModals" class="btn-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Line Item *</label>
            <select v-model.number="form.business_case_line_item_id" required>
              <option :value="0" disabled>Select a line item</option>
              <option v-for="li in lineItems" :key="li.id" :value="li.id">
                {{ li.title }} ({{ li.spend_category }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>WBS Code *</label>
            <input v-model="form.wbs_code" type="text" placeholder="e.g., WBS-2025-001" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Optional description"></textarea>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="form.status">
              <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="form-group">
            <p style="font-size: 0.85rem; color: #666; margin: 0;">
              <strong>Note:</strong> Owner Group will be automatically inherited from the selected Line Item.
            </p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeModals" class="btn-secondary">Cancel</button>
          <button @click="createItem" class="btn-primary">Create</button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Edit WBS</h2>
          <button @click="closeModals" class="btn-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>Line Item</label>
            <input :value="getLineItemTitle(form.business_case_line_item_id)" type="text" disabled />
            <p style="font-size: 0.85rem; color: #666; margin: 0.25rem 0 0 0;">Cannot change parent entity</p>
          </div>
          <div class="form-group">
            <label>WBS Code *</label>
            <input v-model="form.wbs_code" type="text" required />
          </div>
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="form.status">
              <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Owner Group (Inherited)</label>
            <input :value="getGroupName(form.owner_group_id)" type="text" disabled />
            <p style="font-size: 0.85rem; color: #666; margin: 0.25rem 0 0 0;">Inherited from parent Line Item</p>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeModals" class="btn-secondary">Cancel</button>
          <button @click="updateItem" class="btn-primary">Update</button>
        </div>
      </div>
    </div>
  </div>
</template>
