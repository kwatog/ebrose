# Ebrose Component Library Specification

## Design Principles

1. **Composable**: Components accept slots and can be nested
2. **Accessible**: ARIA labels, keyboard navigation, focus management
3. **Typed**: Full TypeScript/Vue 3 type support
4. **Themeable**: Use CSS variables from design system
5. **Responsive**: Mobile-first, touch-friendly
6. **Testable**: Clear props, events, and DOM structure

---

## Component Specifications

### 1. BaseButton

**Purpose**: Primary interactive element for user actions

**Props**:
```typescript
{
  variant: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success'
  size: 'xs' | 'sm' | 'md' | 'lg'
  loading: boolean
  disabled: boolean
  icon: Component (optional - Heroicon)
  iconRight: Component (optional - Heroicon for right-side icon)
  type: 'button' | 'submit' | 'reset'
  fullWidth: boolean
}
```

**Events**:
- `@click` - Emitted on button click (not emitted if loading/disabled)

**Slots**:
- `default` - Button text/content
- `icon` - Custom icon slot (overrides icon prop)

**Accessibility**:
- ARIA `aria-busy` when loading
- ARIA `aria-disabled` when disabled
- Focus visible ring
- Keyboard Enter/Space activation

**Styling**:
- **Primary**: Green background, white text, shadow on hover
- **Secondary**: Gray border, transparent background
- **Ghost**: No border, hover background
- **Danger**: Red background for destructive actions
- **Success**: Green background for confirmations

**Loading State**:
- Shows spinner icon
- Disables button interaction
- Maintains button width (prevents layout shift)

---

### 2. BaseInput

**Purpose**: Text input field with validation states

**Props**:
```typescript
{
  modelValue: string | number
  type: 'text' | 'email' | 'number' | 'password' | 'date' | 'search'
  label: string
  placeholder: string
  helpText: string
  error: string
  disabled: boolean
  required: boolean
  prefixIcon: Component (Heroicon)
  suffixIcon: Component (Heroicon)
  maxlength: number
}
```

**Events**:
- `@update:modelValue` - v-model support
- `@focus` - Input focused
- `@blur` - Input blurred
- `@input` - Value changed

**Slots**:
- `prefix` - Content before input
- `suffix` - Content after input

**States**:
- **Default**: Gray border
- **Focus**: Primary color border + ring
- **Error**: Red border + error message below
- **Disabled**: Gray background, reduced opacity

**Accessibility**:
- Label associated with input via `for` attribute
- Error messages use `aria-describedby`
- Required fields marked with `aria-required`
- Proper input types for mobile keyboards

---

### 3. BaseSelect

**Purpose**: Dropdown selection field

**Props**:
```typescript
{
  modelValue: string | number | array
  options: Array<{ value: string | number, label: string, disabled?: boolean }>
  label: string
  placeholder: string
  error: string
  disabled: boolean
  required: boolean
  multiple: boolean
  searchable: boolean
}
```

**Events**:
- `@update:modelValue` - v-model support
- `@change` - Selection changed

**Features**:
- Search/filter options (if searchable)
- Keyboard navigation (arrow keys)
- Multi-select with checkboxes
- Clear all button
- Empty state message

**Accessibility**:
- ARIA `role="listbox"` for dropdown
- ARIA `aria-expanded` for open/closed state
- Keyboard navigation (Up/Down arrows, Enter, Escape)

---

### 4. BaseTextarea

**Purpose**: Multi-line text input

**Props**:
```typescript
{
  modelValue: string
  label: string
  placeholder: string
  helpText: string
  error: string
  disabled: boolean
  required: boolean
  rows: number (default: 4)
  maxlength: number
  autoResize: boolean
  showCount: boolean
}
```

**Events**:
- `@update:modelValue` - v-model support
- `@focus`, `@blur`, `@input`

**Features**:
- Auto-resize height based on content
- Character counter (if maxlength set)
- Resizable handle (CSS)

---

### 5. BaseModal

**Purpose**: Overlay dialog for forms, confirmations, content

**Props**:
```typescript
{
  modelValue: boolean (show/hide)
  size: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  title: string
  closeOnBackdrop: boolean (default: true)
  closeOnEscape: boolean (default: true)
  showClose: boolean (default: true)
  persistent: boolean (prevent closing)
}
```

**Events**:
- `@update:modelValue` - v-model support
- `@close` - Modal closed (any method)
- `@open` - Modal opened

**Slots**:
- `header` - Custom header content (overrides title prop)
- `default` - Modal body content
- `footer` - Footer actions (buttons)

**Features**:
- Focus trap (tab cycles through modal only)
- Restore focus to trigger element on close
- Backdrop blur effect
- Slide-in animation
- Body scroll lock when open
- Stacked modals (z-index management)

**Accessibility**:
- ARIA `role="dialog"`
- ARIA `aria-modal="true"`
- ARIA `aria-labelledby` for title
- Focus management
- Escape key to close

---

### 6. BaseTable

**Purpose**: Data display with sorting, selection

**Props**:
```typescript
{
  columns: Array<{
    key: string
    label: string
    sortable?: boolean
    width?: string
    align?: 'left' | 'center' | 'right'
  }>
  data: Array<Record<string, any>>
  loading: boolean
  selectable: boolean
  stickyHeader: boolean
  emptyMessage: string
}
```

**Events**:
- `@row-click` - Row clicked
- `@selection-change` - Selected rows changed
- `@sort` - Sort column/direction changed

**Slots**:
- `column-{key}` - Custom column cell renderer
- `actions` - Action column (edit, delete buttons)
- `empty` - Empty state content
- `loading` - Loading state content

**Features**:
- Column sorting (click header)
- Row selection (checkboxes)
- Sticky header on scroll
- Responsive horizontal scroll
- Hover row highlight
- Zebra striping (optional)

**Accessibility**:
- Proper table semantics (thead, tbody, th, td)
- Sort buttons in headers with ARIA labels
- Row selection with proper checkbox labels

---

### 7. BaseBadge

**Purpose**: Status indicators, tags, labels

**Props**:
```typescript
{
  variant: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  size: 'sm' | 'md' | 'lg'
  dot: boolean (show dot indicator instead of text)
  removable: boolean (show X button)
}
```

**Events**:
- `@remove` - X button clicked

**Slots**:
- `default` - Badge content

**Variants**:
- **Primary**: Green
- **Success**: Green (semantic)
- **Warning**: Orange/Yellow
- **Error**: Red
- **Info**: Blue
- **Secondary**: Gray

---

### 8. BaseCard

**Purpose**: Content container with consistent styling

**Props**:
```typescript
{
  title: string
  subtitle: string
  padding: 'none' | 'sm' | 'md' | 'lg'
  hoverable: boolean (lift on hover)
  clickable: boolean (cursor pointer)
}
```

**Events**:
- `@click` - Card clicked (if clickable)

**Slots**:
- `header` - Custom header (overrides title/subtitle)
- `default` - Card body
- `footer` - Card footer

---

### 9. LoadingSpinner

**Purpose**: Loading indicator

**Props**:
```typescript
{
  size: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  color: 'primary' | 'white' | 'gray'
  label: string (accessibility label)
}
```

**Implementation**:
- SVG spinner with CSS animation
- Smooth rotation
- ARIA `role="status"` with sr-only label

---

### 10. EmptyState

**Purpose**: Placeholder for empty data lists

**Props**:
```typescript
{
  icon: Component (Heroicon)
  title: string
  description: string
  actionText: string
  actionIcon: Component
}
```

**Events**:
- `@action` - Action button clicked

**Slots**:
- `icon` - Custom icon
- `default` - Full custom content
- `actions` - Custom action buttons

**Design**:
- Centered layout
- Large icon (muted color)
- Descriptive text
- Optional CTA button

---

### 11. BaseDropdown

**Purpose**: Dropdown menu for navigation/actions

**Props**:
```typescript
{
  placement: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end'
  disabled: boolean
  closeOnClick: boolean
}
```

**Events**:
- `@open` - Dropdown opened
- `@close` - Dropdown closed

**Slots**:
- `trigger` - Button/element that opens dropdown
- `default` - Dropdown menu content

**Features**:
- Click outside to close
- Escape key to close
- Keyboard navigation (arrow keys)
- Auto-positioning (flip if near edge)
- Smooth slide-in animation

**Usage Example**:
```vue
<BaseDropdown>
  <template #trigger>
    <BaseButton>Menu</BaseButton>
  </template>
  <div class="dropdown-menu">
    <a href="/profile">Profile</a>
    <a href="/settings">Settings</a>
    <button @click="logout">Logout</button>
  </div>
</BaseDropdown>
```

---

## Design Token Usage

All components must use CSS variables from `main.css`:

```css
/* Colors */
var(--color-primary)
var(--color-success)
var(--color-error)
var(--color-gray-100) through var(--color-gray-900)

/* Spacing */
var(--spacing-1) through var(--spacing-16)

/* Typography */
var(--text-xs) through var(--text-4xl)
var(--font-normal, --font-medium, --font-semibold, --font-bold)

/* Shadows */
var(--shadow-sm, --shadow-md, --shadow-lg)

/* Border Radius */
var(--radius-sm, --radius-md, --radius-lg, --radius-xl, --radius-full)

/* Transitions */
var(--transition-fast, --transition-base, --transition-slow)

/* Z-Index */
var(--z-dropdown, --z-modal, --z-tooltip)
```

---

## Coding Standards

### Template Structure
```vue
<template>
  <div :class="rootClasses">
    <!-- Component content -->
  </div>
</template>
```

### Script Setup
```vue
<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  // Props with defaults
}

const props = withDefaults(defineProps<Props>(), {
  // defaults
})

const emit = defineEmits<{
  // events
}>()

// Computed classes
const rootClasses = computed(() => ({
  // conditional classes
}))
</script>
```

### Style (Scoped)
```vue
<style scoped>
/* Use design tokens, not hardcoded values */
.component {
  padding: var(--spacing-4);
  color: var(--color-text);
  /* ... */
}
</style>
```

---

## Component Dependencies

### Required Heroicons
```typescript
import {
  XMarkIcon,          // Close buttons, remove
  ChevronDownIcon,    // Dropdowns, selects
  CheckIcon,          // Success, checkboxes
  ExclamationTriangleIcon, // Warnings
  ExclamationCircleIcon,   // Errors
  InformationCircleIcon,   // Info
  MagnifyingGlassIcon,     // Search
  PlusIcon,           // Add/Create
  PencilIcon,         // Edit
  TrashIcon,          // Delete
  ArrowPathIcon,      // Loading/Refresh
} from '@heroicons/vue/24/outline'

import {
  CheckCircleIcon,    // Solid success
  XCircleIcon,        // Solid error
} from '@heroicons/vue/24/solid'
```

---

## Testing Strategy

Each component should be testable via:

1. **Unit Tests** (Vitest):
   - Props render correctly
   - Events emit properly
   - Computed properties work
   - Edge cases handled

2. **E2E Tests** (Playwright):
   - User interactions work
   - Accessibility features functional
   - Visual regression tests
   - Keyboard navigation

3. **Type Safety**:
   - Full TypeScript coverage
   - Proper prop types
   - Event type definitions

---

## Implementation Priority

### Phase 1 - Critical Components (Build First)
1. **BaseButton** - Most used, needed everywhere
2. **BaseInput** - Forms depend on this
3. **BaseModal** - Existing modals need replacement
4. **LoadingSpinner** - Loading states everywhere

### Phase 2 - Common Components
5. **BaseSelect** - Many forms use dropdowns
6. **BaseBadge** - Status indicators common
7. **BaseCard** - Layout component
8. **EmptyState** - Better UX for empty lists

### Phase 3 - Advanced Components
9. **BaseTable** - Complex, many features
10. **BaseTextarea** - Less common than Input
11. **BaseDropdown** - Navigation menus

---

## Migration Strategy

### Step 1: Build Components
Create all components in `components/base/`

### Step 2: Add to Auto-Imports (Optional)
Nuxt 3 auto-imports components, but can explicitly configure:

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  components: [
    {
      path: '~/components/base',
      prefix: 'Base'
    }
  ]
})
```

### Step 3: Page Migration Pattern
For each page:

1. Import new components
2. Replace old HTML with components
3. Remove inline styles
4. Use design tokens
5. Test functionality
6. Update E2E tests

### Step 4: Remove Legacy Code
After all pages migrated:
- Remove old modal implementations
- Clean up duplicate styles
- Update documentation

---

## Example: Before/After

### Before (Current)
```vue
<template>
  <button
    class="btn-primary"
    @click="handleClick"
    :disabled="loading"
  >
    {{ loading ? 'Loading...' : 'Submit' }}
  </button>
</template>
```

### After (With BaseButton)
```vue
<template>
  <BaseButton
    variant="primary"
    :loading="loading"
    @click="handleClick"
  >
    Submit
  </BaseButton>
</template>
```

---

## Success Criteria

✅ All components built and documented
✅ Components use design tokens consistently
✅ Accessibility features implemented
✅ TypeScript types defined
✅ No console errors/warnings
✅ Components work in existing pages
✅ E2E tests pass with new components
✅ Responsive on mobile/tablet/desktop
