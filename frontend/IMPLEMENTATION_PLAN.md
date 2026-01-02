# Ebrose Frontend - Phase 2 Implementation Plan

**Status**: Phase 1 Complete ✅ | Planning Phase 2 Enhancements
**Date**: January 2, 2026
**Version**: 2.0.0

---

## Phase 1 Recap (100% Complete)

### Achievements
- ✅ **11 Base Components** - Complete component library
- ✅ **13 Pages Migrated** - All pages using new design system
- ✅ **75/75 E2E Tests** - 100% test coverage
- ✅ **789-line CSS Design System** - Comprehensive design tokens
- ✅ **Heroicons Navigation** - Professional icon system
- ✅ **Mobile Responsive** - Hamburger menu and responsive design
- ✅ **Full Documentation** - README, specs, and completion reports

---

## Phase 2: Enhanced Features & User Experience

### Priority 1: Excel Export (High Business Value)

**Objective**: Enable users to export data tables to Excel format for external analysis and reporting.

**Scope**:
- All data grid pages (Budget Items, Purchase Orders, WBS, Assets, etc.)
- Support for filtered/sorted data export
- Preserve column formatting and data types
- Include metadata (export date, user, filters applied)

**Technical Implementation**:

1. **Install Dependencies**
   ```bash
   npm install xlsx
   npm install --save-dev @types/xlsx
   ```

2. **Create Export Composable** - `composables/useExcelExport.ts`
   ```typescript
   export const useExcelExport = () => {
     const exportToExcel = (data: any[], filename: string, sheetName: string) => {
       // Implementation with xlsx library
     }

     const exportTableToExcel = (tableData: any[], columns: any[], filename: string) => {
       // Map columns to Excel format
     }

     return { exportToExcel, exportTableToExcel }
   }
   ```

3. **Add Export Button to BaseTable Component**
   - Add optional `exportable` prop
   - Add download icon button to table header
   - Trigger export with current data/filters

4. **Update Pages**
   - Budget Items: Export with fiscal year and group filters
   - Purchase Orders: Export with access levels
   - Assets: Export with depreciation calculations
   - WBS: Export hierarchical structure (flattened)
   - All other data pages

**Deliverables**:
- ✅ Excel export composable
- ✅ BaseTable export integration
- ✅ Export functionality on all 10 data pages
- ✅ E2E tests for export functionality
- ✅ Documentation in README

**Estimated Effort**: 4-6 hours

---

### Priority 2: Complete Icon Migration

**Objective**: Replace all remaining emoji icons with professional Heroicons.

**Scope**:
- Dashboard stat cards (💰, 💸, 📦, 👥 → Heroicons)
- Quick action buttons (💰, 📋, 📦, 🧾 → Heroicons)
- Page headers and empty states
- Any remaining emoji usage

**Technical Implementation**:

1. **Extend useIcons Composable**
   ```typescript
   // Add dashboard-specific icons
   'budget': BanknotesIcon,
   'spending': CreditCardIcon,
   'orders': ShoppingCartIcon,
   'resources': UsersIcon,
   'business-case': DocumentTextIcon,
   'receipt': ReceiptRefundIcon,
   // ... more mappings
   ```

2. **Update Dashboard Components** - `pages/index.vue`
   - Replace emoji stat card icons
   - Update quick action icons
   - Ensure consistent sizing

3. **Update Empty States**
   - Replace emoji placeholders with appropriate Heroicons
   - Update EmptyState component to accept icon components

**Deliverables**:
- ✅ Extended icon mappings
- ✅ Dashboard fully icon-migrated
- ✅ All pages using Heroicons
- ✅ Updated screenshots

**Estimated Effort**: 2-3 hours

---

### Priority 3: Dark Mode

**Objective**: Add dark theme toggle for improved accessibility and user preference.

**Scope**:
- Full dark theme with proper color contrast
- User preference persistence (localStorage)
- Smooth theme transitions
- Toggle switch in navigation

**Technical Implementation**:

1. **Extend CSS Design System** - `assets/css/main.css`
   ```css
   :root {
     /* Light theme (existing) */
   }

   [data-theme="dark"] {
     --color-primary: #60a5fa;
     --color-bg: #1f2937;
     --color-surface: #374151;
     --color-text: #f9fafb;
     /* ... all token overrides */
   }
   ```

2. **Create Theme Composable** - `composables/useTheme.ts`
   ```typescript
   export const useTheme = () => {
     const theme = ref<'light' | 'dark'>('light')

     const toggleTheme = () => { /* ... */ }
     const setTheme = (newTheme: 'light' | 'dark') => { /* ... */ }

     onMounted(() => {
       // Load from localStorage or system preference
     })

     return { theme, toggleTheme, setTheme }
   }
   ```

3. **Add Toggle to Navigation** - `layouts/default.vue`
   - Sun/Moon icon toggle button
   - Smooth transition between themes
   - Persist user choice

**Deliverables**:
- ✅ Dark theme CSS tokens
- ✅ Theme composable with persistence
- ✅ Navigation toggle component
- ✅ All components dark-mode compatible
- ✅ E2E tests for theme switching
- ✅ Documentation

**Estimated Effort**: 6-8 hours

---

### Priority 4: Advanced Charts (Budget Visualization)

**Objective**: Add interactive charts for budget and spending visualization.

**Scope**:
- Dashboard budget utilization chart (replace progress bar)
- Budget Items: spending trends over time
- Purchase Orders: spending by category
- Interactive tooltips and legends

**Technical Implementation**:

1. **Install Chart.js**
   ```bash
   npm install chart.js vue-chartjs
   ```

2. **Create Chart Components**
   - `components/charts/BudgetUtilizationChart.vue` - Donut/Pie chart
   - `components/charts/SpendingTrendChart.vue` - Line chart
   - `components/charts/CategoryBreakdownChart.vue` - Bar chart

3. **Update Dashboard** - `pages/index.vue`
   - Replace simple progress bar with donut chart
   - Add spending trend (last 6 months)
   - Interactive tooltips

4. **Add Chart Views to Budget Pages**
   - Budget Items: Add "Chart View" toggle
   - Show spending trends and comparisons

**Deliverables**:
- ✅ Chart.js integration
- ✅ 3 reusable chart components
- ✅ Dashboard chart views
- ✅ Budget page chart views
- ✅ Responsive chart sizing
- ✅ E2E tests for chart rendering

**Estimated Effort**: 8-10 hours

---

### Priority 5: PDF Export

**Objective**: Generate PDF reports for budget summaries and audit logs.

**Scope**:
- Budget summary reports
- Audit log exports
- Purchase order PDFs
- Professional formatting with company branding

**Technical Implementation**:

1. **Install jsPDF**
   ```bash
   npm install jspdf jspdf-autotable
   npm install --save-dev @types/jspdf
   ```

2. **Create PDF Composable** - `composables/usePDFExport.ts`
   ```typescript
   export const usePDFExport = () => {
     const generateBudgetReport = (budgetData: any[]) => { /* ... */ }
     const generateAuditReport = (auditLogs: any[]) => { /* ... */ }
     const generatePurchaseOrder = (po: any) => { /* ... */ }

     return { generateBudgetReport, generateAuditReport, generatePurchaseOrder }
   }
   ```

3. **Add PDF Export Buttons**
   - Admin Audit page: "Export to PDF"
   - Budget Items: "Generate Budget Report"
   - Purchase Orders: "Print PO" (individual)

4. **PDF Templates**
   - Header with logo and company name
   - Table formatting
   - Page numbers and metadata
   - Professional styling

**Deliverables**:
- ✅ PDF export composable
- ✅ PDF templates for 3 report types
- ✅ Export buttons on relevant pages
- ✅ E2E tests for PDF generation
- ✅ Documentation

**Estimated Effort**: 6-8 hours

---

### Priority 6: Real-time Updates (WebSocket)

**Objective**: Enable live updates for collaborative editing and system notifications.

**Scope**:
- Real-time notifications for record changes
- Live updates when other users edit data
- Connection status indicator
- Optimistic UI updates

**Technical Implementation**:

1. **Backend WebSocket Setup** (requires backend work)
   - Add WebSocket endpoint to FastAPI
   - Emit events on CRUD operations
   - Room-based subscriptions (by page/entity type)

2. **Frontend WebSocket Composable** - `composables/useWebSocket.ts`
   ```typescript
   export const useWebSocket = () => {
     const socket = ref<WebSocket | null>(null)
     const isConnected = ref(false)

     const connect = () => { /* ... */ }
     const subscribe = (channel: string, callback: Function) => { /* ... */ }
     const disconnect = () => { /* ... */ }

     return { socket, isConnected, connect, subscribe, disconnect }
   }
   ```

3. **Update Pages for Live Data**
   - Budget Items: Auto-refresh on remote changes
   - Purchase Orders: Show "User X is editing" indicators
   - Audit Logs: Live log streaming

4. **Add Connection Indicator**
   - Navigation bar indicator (green dot when connected)
   - Reconnection logic with exponential backoff

**Deliverables**:
- ✅ Backend WebSocket endpoints
- ✅ Frontend WebSocket composable
- ✅ Live updates on 3+ pages
- ✅ Connection status indicator
- ✅ E2E tests for real-time features
- ✅ Documentation

**Estimated Effort**: 10-12 hours (including backend)

---

### Priority 7: Progressive Web App (PWA) - Offline Mode

**Objective**: Enable offline functionality and app-like experience.

**Scope**:
- Service worker for offline caching
- Offline data access (read-only)
- Install prompt for mobile/desktop
- Sync queue for offline edits

**Technical Implementation**:

1. **Install Nuxt PWA Module**
   ```bash
   npm install @vite-pwa/nuxt
   ```

2. **Configure PWA** - `nuxt.config.ts`
   ```typescript
   modules: ['@vite-pwa/nuxt'],
   pwa: {
     manifest: { /* ... */ },
     workbox: { /* ... */ },
   }
   ```

3. **Offline Data Strategy**
   - Cache API responses in IndexedDB
   - Read-only access when offline
   - Queue mutations for sync when online

4. **Create Offline Indicator**
   - Show "Offline" badge in navigation
   - Disable edit actions when offline
   - Show sync status

**Deliverables**:
- ✅ PWA configuration
- ✅ Service worker with caching strategy
- ✅ Offline data access
- ✅ Install prompt
- ✅ Offline indicator
- ✅ Documentation

**Estimated Effort**: 8-10 hours

---

### Priority 8: Advanced Filters & Saved Presets

**Objective**: Allow users to create and save complex filter combinations.

**Scope**:
- Multi-criteria filtering on all data pages
- Save filter presets (localStorage or backend)
- Quick filter switching
- Share filters with team (URLs with filter params)

**Technical Implementation**:

1. **Create Advanced Filter Component** - `components/base/BaseAdvancedFilter.vue`
   - Multiple filter criteria
   - AND/OR logic
   - Date ranges, numeric ranges, text search
   - Tag-based UI for active filters

2. **Create Filter Preset Composable** - `composables/useFilterPresets.ts`
   ```typescript
   export const useFilterPresets = (pageKey: string) => {
     const presets = ref<FilterPreset[]>([])

     const savePreset = (name: string, filters: any) => { /* ... */ }
     const loadPreset = (id: string) => { /* ... */ }
     const deletePreset = (id: string) => { /* ... */ }
     const sharePreset = (id: string) => { /* URL generation */ }

     return { presets, savePreset, loadPreset, deletePreset, sharePreset }
   }
   ```

3. **Update Data Pages**
   - Add "Advanced Filters" button
   - Show active filters as removable tags
   - Preset dropdown for quick switching

**Deliverables**:
- ✅ Advanced filter component
- ✅ Filter preset composable
- ✅ Integration on all data pages
- ✅ Shareable filter URLs
- ✅ E2E tests for filtering
- ✅ Documentation

**Estimated Effort**: 6-8 hours

---

### Priority 9: Bulk Operations

**Objective**: Enable bulk edit and delete operations for efficiency.

**Scope**:
- Multi-select on all data tables
- Bulk delete with confirmation
- Bulk edit (change owner group, status, etc.)
- Bulk export (already covered by Excel export)

**Technical Implementation**:

1. **Extend BaseTable Component**
   - Already has `selectable` prop
   - Add `selectedRows` v-model binding
   - Add bulk action toolbar (appears when rows selected)

2. **Create Bulk Action Toolbar** - `components/base/BulkActionBar.vue`
   ```vue
   <template>
     <div v-if="selectedCount > 0" class="bulk-action-bar">
       <span>{{ selectedCount }} selected</span>
       <BaseButton variant="ghost" @click="$emit('deselect-all')">
         Clear
       </BaseButton>
       <BaseButton variant="danger" @click="$emit('bulk-delete')">
         Delete Selected
       </BaseButton>
       <BaseButton variant="secondary" @click="$emit('bulk-edit')">
         Edit Selected
       </BaseButton>
     </div>
   </template>
   ```

3. **Add Bulk Operations to Pages**
   - Budget Items: Bulk delete, bulk change owner group
   - Purchase Orders: Bulk status change
   - Assets: Bulk depreciation update

4. **Bulk Edit Modal**
   - Show editable fields (only common fields)
   - Preview changes before applying
   - Confirmation step

**Deliverables**:
- ✅ Enhanced BaseTable with bulk selection
- ✅ BulkActionBar component
- ✅ Bulk delete on all data pages
- ✅ Bulk edit modal and logic
- ✅ E2E tests for bulk operations
- ✅ Documentation

**Estimated Effort**: 6-8 hours

---

### Priority 10: Custom Themes

**Objective**: Allow users to customize the color scheme and branding.

**Scope**:
- Theme customizer UI
- Predefined theme presets (Professional, Ocean, Forest, Sunset)
- Custom color picker for primary/accent colors
- Save user theme preference

**Technical Implementation**:

1. **Create Theme Customizer** - `components/admin/ThemeCustomizer.vue`
   - Color pickers for primary, accent, success, warning, danger
   - Preview panel
   - Reset to default
   - Save/load themes

2. **Extend Theme Composable** - `composables/useTheme.ts`
   ```typescript
   const customColors = ref({
     primary: '#2563eb',
     accent: '#8b5cf6',
     // ...
   })

   const applyCustomTheme = (colors: ThemeColors) => {
     document.documentElement.style.setProperty('--color-primary', colors.primary)
     // ... apply all custom colors
   }
   ```

3. **Add Theme Presets**
   - Professional (current blue)
   - Ocean (teal/cyan)
   - Forest (green/emerald)
   - Sunset (orange/red)
   - Corporate (gray/blue)

4. **Add Settings Page** - `pages/settings.vue`
   - Theme customizer
   - Language preferences (future)
   - Notification settings (future)

**Deliverables**:
- ✅ Theme customizer component
- ✅ 5 predefined theme presets
- ✅ Custom color application logic
- ✅ Settings page
- ✅ Theme persistence
- ✅ E2E tests
- ✅ Documentation

**Estimated Effort**: 8-10 hours

---

## Implementation Roadmap

### Sprint 1 (Week 1)
**Focus**: High Business Value Features
- ✅ **Excel Export** (Priority 1) - 4-6 hours
- ✅ **Complete Icon Migration** (Priority 2) - 2-3 hours
- ✅ **Advanced Filters** (Priority 8) - 6-8 hours

**Total**: ~15 hours

### Sprint 2 (Week 2)
**Focus**: User Experience Enhancements
- ✅ **Dark Mode** (Priority 3) - 6-8 hours
- ✅ **Bulk Operations** (Priority 9) - 6-8 hours

**Total**: ~15 hours

### Sprint 3 (Week 3)
**Focus**: Data Visualization & Reporting
- ✅ **Advanced Charts** (Priority 4) - 8-10 hours
- ✅ **PDF Export** (Priority 5) - 6-8 hours

**Total**: ~16 hours

### Sprint 4 (Week 4)
**Focus**: Advanced Features
- ✅ **Real-time Updates** (Priority 6) - 10-12 hours
- ✅ **Custom Themes** (Priority 10) - 8-10 hours

**Total**: ~20 hours

### Sprint 5 (Week 5)
**Focus**: Progressive Enhancement
- ✅ **PWA/Offline Mode** (Priority 7) - 8-10 hours
- ✅ **Final Testing & Documentation** - 4-6 hours

**Total**: ~14 hours

---

## Testing Strategy

Each priority item includes:
1. **Unit Tests** (Vitest) for composables and utilities
2. **Component Tests** for new UI components
3. **E2E Tests** (Playwright) for user workflows
4. **Screenshot Tests** for visual regression

**Target**: Maintain 100% E2E test coverage

---

## Documentation Requirements

For each completed priority:
1. Update README.md with new features
2. Add usage examples to COMPONENT_SPECS.md
3. Update UI_REDESIGN_COMPLETE.md
4. Create migration guide if breaking changes

---

## Success Metrics

### Phase 2 Completion Criteria:
- ✅ All 10 priorities implemented
- ✅ 100+ E2E tests passing
- ✅ All new features documented
- ✅ Performance budget maintained (< 2s initial load)
- ✅ Accessibility audit passing (WCAG 2.1 AA)
- ✅ Zero console errors/warnings
- ✅ Browser compatibility verified

### Optional Stretch Goals:
- 🎯 Multi-language support (i18n)
- 🎯 Advanced role-based UI customization
- 🎯 Integration with external calendar for scheduling
- 🎯 Mobile native app (React Native/Capacitor)
- 🎯 Desktop app (Tauri/Electron)

---

## Resource Requirements

### Dependencies to Install:
```json
{
  "dependencies": {
    "xlsx": "^0.18.5",
    "chart.js": "^4.4.0",
    "vue-chartjs": "^5.3.0",
    "jspdf": "^2.5.1",
    "jspdf-autotable": "^3.8.2",
    "@vite-pwa/nuxt": "^0.4.0"
  },
  "devDependencies": {
    "@types/xlsx": "^0.0.36",
    "@types/jspdf": "^2.0.0"
  }
}
```

### Backend Changes Required:
- WebSocket endpoint for real-time updates
- Filter preset storage endpoints (optional, can use localStorage)
- Theme storage endpoints (optional, can use localStorage)

---

## Risk Assessment

### Low Risk:
- Excel Export
- Icon Migration
- Dark Mode
- Advanced Filters
- Bulk Operations
- Custom Themes

### Medium Risk:
- Advanced Charts (performance with large datasets)
- PDF Export (complex layouts)

### High Risk:
- Real-time Updates (requires backend changes, connection handling)
- PWA/Offline Mode (complex sync logic, IndexedDB management)

### Mitigation Strategies:
1. **Incremental rollout** - Feature flags for gradual deployment
2. **Performance monitoring** - Track bundle size and load times
3. **Fallback UI** - Graceful degradation for unsupported features
4. **Comprehensive testing** - Especially for real-time and offline features

---

## Conclusion

This implementation plan provides a structured approach to enhancing the Ebrose frontend with high-value features. The phased approach allows for:

1. **Early value delivery** (Excel export first)
2. **Risk management** (complex features later)
3. **User feedback integration** (after each sprint)
4. **Maintainable code quality** (testing throughout)

**Estimated Total Effort**: 80-90 hours (10-12 days)

**Recommended Approach**: Execute sprints sequentially with stakeholder review after each sprint to adjust priorities based on user feedback.

---

**Last Updated**: January 2, 2026
**Status**: 📋 Planning Phase
**Next Step**: Stakeholder review and sprint prioritization
