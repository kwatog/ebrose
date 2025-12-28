<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

interface Asset {
  id: number
  wbs_id: number
  asset_code: string
  asset_type?: string
  description?: string
  owner_group_id: number
  status?: string
  created_by?: number
  updated_by?: number
  created_at?: string
  updated_at?: string
}

interface WBS {
  id: number
  wbs_code: string
  description?: string
}

interface Group {
  id: number
  name: string
}

const userCookie = useCookie('user_info')
const user = computed(() => userCookie.value)

const items = ref<Asset[]>([])
const wbsItems = ref<WBS[]>([])
const groups = ref<Group[]>([])

const showCreateModal = ref(false)
const showEditModal = ref(false)

const form = ref({
  wbs_id: 0,
  asset_code: '',
  asset_type: 'CAPEX',
  description: '',
  owner_group_id: 0,
  status: 'Active'
})

const editingItem = ref<Asset | null>(null)

// Filters
const filterStatus = ref('')
const filterWBS = ref(0)
const filterAssetType = ref('')

const statuses = ['Active', 'Inactive', 'Disposed', 'Under Maintenance']
const assetTypes = ['CAPEX', 'OPEX', 'Lease']

// Fetch data
const fetchItems = async () => {
  try {
    const data = await useApiFetch('/assets', { method: 'GET' })
    items.value = data as Asset[]
  } catch (e: any) {
    alert(`Failed to fetch assets: ${e.data?.detail || e.message}`)
  }
}

const fetchWBS = async () => {
  try {
    const data = await useApiFetch('/wbs', { method: 'GET' })
    wbsItems.value = data as WBS[]
  } catch (e: any) {
    console.error('Failed to fetch WBS items:', e)
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
  fetchWBS()
  fetchGroups()
})

// Computed
const filteredItems = computed(() => {
  let result = items.value
  if (filterStatus.value) {
    result = result.filter(item => item.status === filterStatus.value)
  }
  if (filterWBS.value) {
    result = result.filter(item => item.wbs_id === filterWBS.value)
  }
  if (filterAssetType.value) {
    result = result.filter(item => item.asset_type === filterAssetType.value)
  }
  return result
})

// Helpers
const getWBSCode = (id: number) => {
  return wbsItems.value.find(w => w.id === id)?.wbs_code || 'Unknown'
}

const getGroupName = (id: number) => {
  return groups.value.find(g => g.id === id)?.name || 'Unknown'
}

const getStatusColor = (status?: string) => {
  const colors: Record<string, string> = {
    'Active': '#10b981',
    'Inactive': '#6b7280',
    'Disposed': '#ef4444',
    'Under Maintenance': '#f59e0b'
  }
  return colors[status || 'Active'] || '#6b7280'
}

const getAssetTypeColor = (type?: string) => {
  const colors: Record<string, string> = {
    'CAPEX': '#8b5cf6',
    'OPEX': '#3b82f6',
    'Lease': '#10b981'
  }
  return colors[type || 'CAPEX'] || '#6b7280'
}

// Permissions
const canEdit = (item: Asset) => {
  if (!user.value) return false
  if (user.value.role === 'Admin') return true
  if (user.value.role === 'Manager') return true
  return item.created_by === user.value.id
}

const canDelete = (item: Asset) => {
  if (!user.value) return false
  if (user.value.role === 'Admin') return true
  if (user.value.role === 'Manager') return true
  return false
}

// CRUD operations
const openCreateModal = () => {
  form.value = {
    wbs_id: 0,
    asset_code: '',
    asset_type: 'CAPEX',
    description: '',
    owner_group_id: 0,
    status: 'Active'
  }
  showCreateModal.value = true
}

const openEditModal = (item: Asset) => {
  editingItem.value = item
  form.value = {
    wbs_id: item.wbs_id,
    asset_code: item.asset_code,
    asset_type: item.asset_type || 'CAPEX',
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
    if (!form.value.wbs_id) {
      alert('Please select a WBS')
      return
    }
    if (!form.value.asset_code.trim()) {
      alert('Asset Code is required')
      return
    }

    await useApiFetch('/assets', {
      method: 'POST',
      body: form.value
    })
    await fetchItems()
    closeModals()
  } catch (e: any) {
    alert(`Failed to create asset: ${e.data?.detail || e.message}`)
  }
}

const updateItem = async () => {
  if (!editingItem.value) return
  try {
    await useApiFetch(`/assets/${editingItem.value.id}`, {
      method: 'PUT',
      body: {
        asset_code: form.value.asset_code,
        asset_type: form.value.asset_type,
        description: form.value.description,
        status: form.value.status
      }
    })
    await fetchItems()
    closeModals()
  } catch (e: any) {
    alert(`Failed to update asset: ${e.data?.detail || e.message}`)
  }
}

const deleteItem = async (item: Asset) => {
  if (!confirm(`Are you sure you want to delete asset "${item.asset_code}"?`)) return
  try {
    await useApiFetch(`/assets/${item.id}`, { method: 'DELETE' })
    await fetchItems()
  } catch (e: any) {
    alert(`Failed to delete asset: ${e.data?.detail || e.message}`)
  }
}
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1>Assets</h1>
      <button @click="openCreateModal" class="btn-primary">+ Create Asset</button>
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
        <label style="display: block; margin-bottom: 0.25rem; font-size: 0.9rem; color: #666;">WBS</label>
        <select v-model.number="filterWBS" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
          <option :value="0">All WBS</option>
          <option v-for="w in wbsItems" :key="w.id" :value="w.id">{{ w.wbs_code }}</option>
        </select>
      </div>
      <div style="flex: 1; min-width: 200px;">
        <label style="display: block; margin-bottom: 0.25rem; font-size: 0.9rem; color: #666;">Asset Type</label>
        <select v-model="filterAssetType" style="width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px;">
          <option value="">All Types</option>
          <option v-for="t in assetTypes" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>
    </div>

    <!-- List -->
    <div v-if="filteredItems.length === 0" class="empty-state">
      <p>No assets found</p>
      <button @click="openCreateModal" class="btn-primary">Create First Asset</button>
    </div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>Asset Code</th>
            <th>WBS</th>
            <th>Type</th>
            <th>Description</th>
            <th>Owner Group</th>
            <th>Status</th>
            <th>Created By</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td><strong>{{ item.asset_code }}</strong></td>
            <td>{{ getWBSCode(item.wbs_id) }}</td>
            <td>
              <span class="badge" :style="{ backgroundColor: getAssetTypeColor(item.asset_type) }">
                {{ item.asset_type || 'CAPEX' }}
              </span>
            </td>
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
          <h2>Create Asset</h2>
          <button @click="closeModals" class="btn-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>WBS *</label>
            <select v-model.number="form.wbs_id" required>
              <option :value="0" disabled>Select a WBS</option>
              <option v-for="w in wbsItems" :key="w.id" :value="w.id">
                {{ w.wbs_code }}{{ w.description ? ' - ' + w.description : '' }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>Asset Code *</label>
            <input v-model="form.asset_code" type="text" placeholder="e.g., ASSET-2025-001" required />
          </div>
          <div class="form-group">
            <label>Asset Type</label>
            <select v-model="form.asset_type">
              <option v-for="t in assetTypes" :key="t" :value="t">{{ t }}</option>
            </select>
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
              <strong>Note:</strong> Owner Group will be automatically inherited from the selected WBS.
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
          <h2>Edit Asset</h2>
          <button @click="closeModals" class="btn-close">&times;</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>WBS</label>
            <input :value="getWBSCode(form.wbs_id)" type="text" disabled />
            <p style="font-size: 0.85rem; color: #666; margin: 0.25rem 0 0 0;">Cannot change parent entity</p>
          </div>
          <div class="form-group">
            <label>Asset Code *</label>
            <input v-model="form.asset_code" type="text" required />
          </div>
          <div class="form-group">
            <label>Asset Type</label>
            <select v-model="form.asset_type">
              <option v-for="t in assetTypes" :key="t" :value="t">{{ t }}</option>
            </select>
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
            <p style="font-size: 0.85rem; color: #666; margin: 0.25rem 0 0 0;">Inherited from parent WBS</p>
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
