<script setup lang="ts">
import {
  BanknotesIcon,
  ChartPieIcon,
  DocumentIcon,
  UsersIcon,
  ClipboardIcon,
  ChartBarIcon,
  CubeIcon,
} from '@heroicons/vue/24/outline'

interface DashboardGroup {
  id: number
  name: string
}

interface DashboardSummary {
  current_year: number
  previous_year: number
  group?: DashboardGroup | null
  groups: DashboardGroup[]
  budgets: {
    current_year_total: string
    previous_year_total: string
    current_year_count: number
    previous_year_count: number
  }
  spend: {
    current_year_total: string
    previous_year_total: string
  }
  open_pos: {
    count: number
    value: string
  }
  recent_grs_count: number
  active_resources_count: number
  pending_business_cases: number
}

const userCookie = useCookie('user_info')
const userData = ref<Record<string, any> | null>(null)
const selectedGroupId = ref<number | null>(null)

const summary = ref<DashboardSummary | null>(null)

const recentGoodsReceipts = ref<any[]>([])
const recentPurchaseOrders = ref<any[]>([])

const loading = ref(true)
const error = ref<string | null>(null)

const groupOptions = computed(() => summary.value?.groups.map(group => ({
  value: group.id,
  label: group.name
})) || [])

const selectedGroupName = computed(() => summary.value?.group?.name || 'Unknown')

const currentYear = computed(() => summary.value?.current_year || new Date().getFullYear())
const previousYear = computed(() => summary.value?.previous_year || (currentYear.value - 1))

const stats = computed(() => ({
  totalBudget: summary.value?.budgets.current_year_total || '0',
  previousBudget: summary.value?.budgets.previous_year_total || '0',
  currentBudgetCount: summary.value?.budgets.current_year_count || 0,
  previousBudgetCount: summary.value?.budgets.previous_year_count || 0,
  totalSpend: summary.value?.spend.current_year_total || '0',
  previousSpend: summary.value?.spend.previous_year_total || '0',
  openPOsCount: summary.value?.open_pos.count || 0,
  openPOsValue: summary.value?.open_pos.value || '0',
  recentGRsCount: summary.value?.recent_grs_count || 0,
  activeResourcesCount: summary.value?.active_resources_count || 0,
  pendingBusinessCases: summary.value?.pending_business_cases || 0
}))

const currentBudgetValue = computed(() => parseFloat(stats.value.totalBudget) || 0)
const currentSpendValue = computed(() => parseFloat(stats.value.totalSpend) || 0)

const utilizationTitle = computed(() => (
  `Budget Utilization · ${selectedGroupName.value} · FY${currentYear.value}`
))

const fetchDashboardSummary = async (groupId?: number | null) => {
  const params = new URLSearchParams()
  if (groupId) {
    params.set('owner_group_id', String(groupId))
  }
  const query = params.toString()
  const res = await useApiFetch<DashboardSummary>(`/dashboard/summary${query ? `?${query}` : ''}`)
  summary.value = res as any
  const resolvedGroupId = summary.value?.group?.id ?? null
  if (resolvedGroupId !== selectedGroupId.value) {
    selectedGroupId.value = resolvedGroupId
  }
}

const fetchRecentActivity = async (groupId: number | null) => {
  if (!groupId) {
    recentGoodsReceipts.value = []
    recentPurchaseOrders.value = []
    return
  }

  const [posData, grsData] = await Promise.all([
    useApiFetch(`/purchase-orders/?limit=5&owner_group_id=${groupId}`, { method: 'GET' }).catch(() => []),
    useApiFetch(`/goods-receipts/?limit=5&owner_group_id=${groupId}`, { method: 'GET' }).catch(() => [])
  ])

  const pos = posData as any[]
  const grs = grsData as any[]

  recentPurchaseOrders.value = pos
    .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime())
    .slice(0, 5)

  recentGoodsReceipts.value = grs
    .sort((a, b) => new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime())
    .slice(0, 5)
}

// Fetch all data
const fetchDashboardData = async (groupId?: number | null) => {
  try {
    loading.value = true
    error.value = null

    await fetchDashboardSummary(groupId ?? selectedGroupId.value)
    const resolvedGroupId = summary.value?.group?.id ?? null
    await fetchRecentActivity(resolvedGroupId)
  } catch (e: any) {
    console.error('Dashboard error:', e)
    error.value = 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
}

const handleGroupChange = async () => {
  await fetchDashboardData(selectedGroupId.value)
}

onMounted(() => {
  if (userCookie.value) {
    try {
      const cookieStr = String(userCookie.value).replace(/"/g, '')
      const decoded = decodeURIComponent(atob(cookieStr))
      userData.value = JSON.parse(decoded)
      selectedGroupId.value = userData.value?.primary_group_id ?? null
    } catch {
      userData.value = null
    }
  }
  fetchDashboardData(selectedGroupId.value)
})

// Helpers
const formatCurrency = (amount: string | number) => {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(num)
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

const getUtilizationPercentage = computed(() => {
  if (currentBudgetValue.value === 0) return 0
  return Math.round((currentSpendValue.value / currentBudgetValue.value) * 100)
})

const getUtilizationColor = computed(() => {
  const pct = getUtilizationPercentage.value
  if (pct < 50) return 'var(--color-success)'
  if (pct < 80) return 'var(--color-warning)'
  return 'var(--color-error)'
})

const isManager = computed(() => {
  return userData.value && ['Admin', 'Manager'].includes(userData.value.role)
})
</script>

<template>
  <div class="main-container">
    <div class="page-header">
      <div>
        <h1 class="page-title">Dashboard</h1>
        <p class="page-subtitle">
          Welcome back, <strong>{{ userData?.full_name || userData?.username }}</strong> ({{ userData?.role }})
        </p>
      </div>
    </div>

    <div v-if="summary" class="scope-bar">
      <div class="scope-info">
        <div class="scope-title">Budget Scope</div>
        <div class="scope-subtitle">FY{{ currentYear }} vs FY{{ previousYear }}</div>
      </div>
      <div class="scope-control">
        <BaseSelect
          v-model="selectedGroupId"
          :options="groupOptions"
          label="Owner Group"
          @change="handleGroupChange"
        />
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <BaseLoadingSpinner size="lg" label="Loading dashboard data..." />
      <p class="text-muted">Loading dashboard data...</p>
    </div>

    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
    </div>

    <div v-else>
      <!-- Statistics Cards -->
      <div class="stats-grid">
        <!-- Budget Overview -->
        <BaseCard padding="md" class="stat-card">
          <div class="stat-card-content">
            <div class="stat-icon stat-icon-primary">
              <BanknotesIcon class="stat-icon-svg" />
            </div>
            <div class="stat-details">
              <div class="stat-label">Budget (FY{{ currentYear }})</div>
              <div class="stat-value">{{ formatCurrency(stats.totalBudget) }}</div>
              <div class="stat-meta">Group: {{ selectedGroupName }} · {{ stats.currentBudgetCount }} items</div>
              <div class="stat-meta">Prev FY{{ previousYear }}: {{ formatCurrency(stats.previousBudget) }} · {{ stats.previousBudgetCount }} items</div>
            </div>
          </div>
        </BaseCard>

        <!-- Spend Overview -->
        <BaseCard padding="md" class="stat-card">
          <div class="stat-card-content">
            <div class="stat-icon stat-icon-warning">
              <ChartPieIcon class="stat-icon-svg" />
            </div>
            <div class="stat-details">
              <div class="stat-label">Planned Spend (FY{{ currentYear }})</div>
              <div class="stat-value">{{ formatCurrency(stats.totalSpend) }}</div>
              <div class="stat-meta" :style="{ color: getUtilizationColor }">
                {{ getUtilizationPercentage }}% of FY{{ currentYear }} budget
              </div>
              <div class="stat-meta">Prev FY{{ previousYear }}: {{ formatCurrency(stats.previousSpend) }}</div>
            </div>
          </div>
        </BaseCard>

        <!-- Open POs -->
        <BaseCard padding="md" class="stat-card">
          <div class="stat-card-content">
            <div class="stat-icon stat-icon-info">
              <DocumentIcon class="stat-icon-svg" />
            </div>
            <div class="stat-details">
              <div class="stat-label">Open Purchase Orders</div>
              <div class="stat-value">{{ stats.openPOsCount }}</div>
              <div class="stat-meta">{{ formatCurrency(stats.openPOsValue) }} value</div>
            </div>
          </div>
        </BaseCard>

        <!-- Active Resources -->
        <BaseCard padding="md" class="stat-card">
          <div class="stat-card-content">
            <div class="stat-icon stat-icon-success">
              <UsersIcon class="stat-icon-svg" />
            </div>
            <div class="stat-details">
              <div class="stat-label">Active Resources</div>
              <div class="stat-value">{{ stats.activeResourcesCount }}</div>
              <div class="stat-meta">{{ stats.recentGRsCount }} GRs this month</div>
            </div>
          </div>
        </BaseCard>

        <!-- Pending Business Cases -->
        <BaseCard v-if="isManager" padding="md" class="stat-card">
          <div class="stat-card-content">
            <div class="stat-icon stat-icon-secondary">
              <ClipboardIcon class="stat-icon-svg" />
            </div>
            <div class="stat-details">
              <div class="stat-label">Pending Business Cases</div>
              <div class="stat-value">{{ stats.pendingBusinessCases }}</div>
              <div class="stat-meta">Awaiting review/approval</div>
            </div>
          </div>
        </BaseCard>
      </div>

      <!-- Budget Utilization Bar -->
      <BaseCard :title="utilizationTitle" padding="md">
        <div class="utilization-bar-container">
          <div class="utilization-bar-bg">
            <div
              class="utilization-bar-fill"
              :style="{
                width: getUtilizationPercentage + '%',
                backgroundColor: getUtilizationColor
              }"
            ></div>
            <div class="utilization-bar-label">
              {{ formatCurrency(stats.totalSpend) }} / {{ formatCurrency(stats.totalBudget) }} ({{ getUtilizationPercentage }}%)
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Quick Actions -->
      <BaseCard title="Quick Actions" padding="md">
        <div class="quick-actions-grid">
          <NuxtLink to="/budget-items" class="quick-action-btn">
            <BanknotesIcon class="quick-action-icon" />
            <span>Manage Budgets</span>
          </NuxtLink>
          <NuxtLink to="/business-cases" class="quick-action-btn">
            <ClipboardIcon class="quick-action-icon" />
            <span>Business Cases</span>
          </NuxtLink>
          <NuxtLink to="/purchase-orders" class="quick-action-btn">
            <DocumentIcon class="quick-action-icon" />
            <span>Purchase Orders</span>
          </NuxtLink>
          <NuxtLink to="/goods-receipts" class="quick-action-btn">
            <CubeIcon class="quick-action-icon" />
            <span>Goods Receipts</span>
          </NuxtLink>
          <NuxtLink v-if="isManager" to="/resources" class="quick-action-btn">
            <UsersIcon class="quick-action-icon" />
            <span>Resources</span>
          </NuxtLink>
          <NuxtLink v-if="isManager" to="/admin/audit" class="quick-action-btn">
            <ChartBarIcon class="quick-action-icon" />
            <span>Audit Logs</span>
          </NuxtLink>
        </div>
      </BaseCard>

      <!-- Recent Activity -->
      <div class="recent-activity-grid">
        <!-- Recent Purchase Orders -->
        <BaseCard title="Recent Purchase Orders" padding="md">
          <BaseEmptyState
            v-if="recentPurchaseOrders.length === 0"
            title="No purchase orders yet"
            description="Purchase orders will appear here once created"
          />
          <div v-else class="recent-items-list">
            <div
              v-for="po in recentPurchaseOrders"
              :key="po.id"
              class="recent-item recent-item-info"
            >
              <div class="recent-item-content">
                <div class="recent-item-title">{{ po.po_number }}</div>
                <div class="recent-item-subtitle">{{ po.supplier || 'No supplier' }}</div>
              </div>
              <div class="recent-item-meta">
                <div class="recent-item-amount recent-item-amount-info">{{ formatCurrency(po.total_amount) }}</div>
                <div class="recent-item-date">{{ formatDate(po.created_at) }}</div>
              </div>
            </div>
          </div>
          <template #footer>
            <NuxtLink to="/purchase-orders" class="view-all-link">
              View all →
            </NuxtLink>
          </template>
        </BaseCard>

        <!-- Recent Goods Receipts -->
        <BaseCard title="Recent Goods Receipts" padding="md">
          <BaseEmptyState
            v-if="recentGoodsReceipts.length === 0"
            title="No goods receipts yet"
            description="Goods receipts will appear here once created"
          />
          <div v-else class="recent-items-list">
            <div
              v-for="gr in recentGoodsReceipts"
              :key="gr.id"
              class="recent-item recent-item-success"
            >
              <div class="recent-item-content">
                <div class="recent-item-title">{{ gr.gr_number }}</div>
                <div class="recent-item-subtitle">{{ gr.description || 'No description' }}</div>
              </div>
              <div class="recent-item-meta">
                <div class="recent-item-amount recent-item-amount-success">{{ formatCurrency(gr.amount) }}</div>
                <div class="recent-item-date">{{ formatDate(gr.created_at) }}</div>
              </div>
            </div>
          </div>
          <template #footer>
            <NuxtLink to="/goods-receipts" class="view-all-link">
              View all →
            </NuxtLink>
          </template>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-12);
  gap: var(--spacing-4);
}

.error-container {
  padding: var(--spacing-6);
  background: var(--color-error-bg);
  border-radius: var(--radius-lg);
}

.error-text {
  color: var(--color-error);
  margin: 0;
}

.scope-bar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-4);
  background: var(--color-gray-50);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-gray-200);
}

.scope-info {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.scope-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-gray-900);
}

.scope-subtitle {
  font-size: var(--text-sm);
  color: var(--color-gray-600);
}

.scope-control {
  min-width: 220px;
}

/* Statistics Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}

.stat-card-content {
  display: flex;
  gap: var(--spacing-4);
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: var(--radius-xl);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: var(--text-2xl);
}

.stat-icon-svg {
  width: 32px;
  height: 32px;
  stroke-width: 1.5;
}

.stat-icon-primary {
  background: var(--color-info-bg);
}

.stat-icon-warning {
  background: var(--color-warning-bg);
}

.stat-icon-info {
  background: var(--color-primary-bg);
}

.stat-icon-success {
  background: var(--color-success-bg);
}

.stat-icon-secondary {
  background: var(--color-secondary-bg);
}

.stat-details {
  flex: 1;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--color-gray-600);
  margin-bottom: var(--spacing-1);
}

.stat-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-gray-900);
  margin-bottom: var(--spacing-1);
}

.stat-meta {
  font-size: var(--text-xs);
  color: var(--color-gray-500);
}

/* Utilization Bar */
.utilization-bar-container {
  margin-top: var(--spacing-4);
}

.utilization-bar-bg {
  background: var(--color-gray-100);
  height: 40px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  position: relative;
}

.utilization-bar-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.utilization-bar-label {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: var(--color-gray-900);
  font-size: var(--text-sm);
}

/* Quick Actions */
.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--spacing-4);
  margin-top: var(--spacing-4);
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-4) var(--spacing-3);
  background: var(--color-gray-50);
  border: 1px solid var(--color-gray-200);
  border-radius: var(--radius-lg);
  text-decoration: none;
  color: var(--color-gray-900);
  font-weight: 500;
  transition: all var(--transition-fast);
  gap: var(--spacing-2);
}

.quick-action-btn:hover {
  background: var(--color-gray-100);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.quick-action-icon {
  width: 28px;
  height: 28px;
  stroke-width: 1.5;
  color: var(--color-primary);
}

/* Recent Activity */
.recent-activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: var(--spacing-4);
}

.recent-items-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: start;
  padding: var(--spacing-3);
  background: var(--color-gray-50);
  border-radius: var(--radius-md);
  border-left: 3px solid;
}

.recent-item-info {
  border-left-color: var(--color-info);
}

.recent-item-success {
  border-left-color: var(--color-success);
}

.recent-item-content {
  flex: 1;
}

.recent-item-title {
  font-weight: 600;
  color: var(--color-gray-900);
  margin-bottom: var(--spacing-1);
  font-size: var(--text-sm);
}

.recent-item-subtitle {
  font-size: var(--text-sm);
  color: var(--color-gray-600);
}

.recent-item-meta {
  text-align: right;
}

.recent-item-amount {
  font-weight: 600;
  margin-bottom: var(--spacing-1);
  font-size: var(--text-sm);
}

.recent-item-amount-info {
  color: var(--color-info);
}

.recent-item-amount-success {
  color: var(--color-success);
}

.recent-item-date {
  font-size: var(--text-xs);
  color: var(--color-gray-500);
}

.view-all-link {
  display: block;
  color: var(--color-primary);
  font-size: var(--text-sm);
  text-decoration: none;
  font-weight: 500;
}

.view-all-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .scope-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .scope-control {
    min-width: auto;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .quick-actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .recent-activity-grid {
    grid-template-columns: 1fr;
  }
}
</style>
