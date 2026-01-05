<script setup lang="ts">
const props = withDefaults(defineProps<{
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info'
  size?: 'sm' | 'md' | 'lg'
  dot?: boolean
  removable?: boolean
}>(), {
  variant: 'primary',
  size: 'md',
  dot: false,
  removable: false
})

const emit = defineEmits<{
  remove: []
}>()

const variantClasses = {
  primary: 'badge-primary',
  secondary: 'badge-secondary',
  success: 'badge-success',
  warning: 'badge-warning',
  error: 'badge-error',
  info: 'badge-info'
}

const sizeClasses = {
  sm: 'badge-sm',
  md: 'badge-md',
  lg: 'badge-lg'
}
</script>

<template>
  <span class="base-badge" :class="[variantClasses[variant], sizeClasses[size]]">
    <span v-if="dot" class="badge-dot"></span>
    <slot />
    <button 
      v-if="removable" 
      class="badge-remove" 
      @click="emit('remove')"
      aria-label="Remove"
    >
      ×
    </button>
  </span>
</template>

<style scoped>
.base-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  font-weight: 500;
  border-radius: var(--radius-full);
  white-space: nowrap;
}

.badge-sm {
  padding: 2px 8px;
  font-size: var(--text-xs);
}

.badge-md {
  padding: 4px 12px;
  font-size: var(--text-sm);
}

.badge-lg {
  padding: 6px 16px;
  font-size: var(--text-base);
}

.badge-primary {
  background: #dcfce7;
  color: #166534;
}

.badge-secondary {
  background: var(--color-gray-100);
  color: var(--color-gray-700);
}

.badge-success {
  background: #dcfce7;
  color: #166534;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.badge-error {
  background: #fee2e2;
  color: #991b1b;
}

.badge-info {
  background: #dbeafe;
  color: #1e40af;
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.badge-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  margin-left: var(--spacing-1);
  background: rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  transition: background var(--transition-fast);
}

.badge-remove:hover {
  background: rgba(0, 0, 0, 0.2);
}
</style>
