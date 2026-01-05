<template>
  <button
    :type="type"
    :class="buttonClasses"
    :disabled="disabled || loading"
    :aria-busy="loading"
    :aria-disabled="disabled"
    @click="handleClick"
  >
    <component
      v-if="loading"
      :is="LoadingIcon"
      class="button-icon button-icon-spin"
      aria-hidden="true"
    />
    <component
      v-else-if="icon && !iconRight"
      :is="icon"
      class="button-icon"
      aria-hidden="true"
    />

    <span v-if="$slots.default" class="button-content">
      <slot />
    </span>

    <component
      v-if="!loading && icon && iconRight"
      :is="icon"
      class="button-icon"
      aria-hidden="true"
    />
  </button>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'

interface Props {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'success'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  icon?: Component
  iconRight?: boolean
  type?: 'button' | 'submit' | 'reset'
  fullWidth?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  iconRight: false,
  type: 'button',
  fullWidth: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const LoadingIcon = ArrowPathIcon

const buttonClasses = computed(() => [
  'base-button',
  `base-button--${props.variant}`,
  `base-button--${props.size}`,
  {
    'base-button--loading': props.loading,
    'base-button--disabled': props.disabled,
    'base-button--full-width': props.fullWidth,
    'base-button--icon-only': props.icon && !slots.default
  }
])

const handleClick = (event: MouseEvent) => {
  if (!props.loading && !props.disabled) {
    emit('click', event)
  }
}

const slots = defineSlots()
</script>

<style scoped>
.base-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  font-family: inherit;
  font-weight: var(--font-semibold);
  border: none;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-decoration: none;
  white-space: nowrap;
  user-select: none;
  position: relative;
}

.base-button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Sizes */
.base-button--xs {
  padding: var(--spacing-1) var(--spacing-3);
  font-size: var(--text-xs);
  border-radius: var(--radius-md);
}

.base-button--sm {
  padding: var(--spacing-2) var(--spacing-4);
  font-size: var(--text-sm);
  border-radius: var(--radius-lg);
}

.base-button--md {
  padding: var(--spacing-3) var(--spacing-5);
  font-size: var(--text-base);
  border-radius: var(--radius-full);
}

.base-button--lg {
  padding: var(--spacing-4) var(--spacing-6);
  font-size: var(--text-lg);
  border-radius: var(--radius-full);
}

/* Icon only buttons */
.base-button--icon-only.base-button--xs {
  padding: var(--spacing-1);
}

.base-button--icon-only.base-button--sm {
  padding: var(--spacing-2);
}

.base-button--icon-only.base-button--md {
  padding: var(--spacing-3);
}

.base-button--icon-only.base-button--lg {
  padding: var(--spacing-4);
}

/* Variants */
.base-button--primary {
  background-color: var(--color-primary);
  color: #ffffff;
}

.base-button--primary:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.base-button--primary:active:not(:disabled) {
  transform: translateY(0);
}

.base-button--secondary {
  background-color: transparent;
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.base-button--secondary:hover:not(:disabled) {
  background-color: var(--color-gray-50);
  border-color: var(--color-gray-300);
}

.base-button--ghost {
  background-color: transparent;
  color: var(--color-text);
}

.base-button--ghost:hover:not(:disabled) {
  background-color: var(--color-gray-100);
}

.base-button--danger {
  background-color: var(--color-error);
  color: #ffffff;
}

.base-button--danger:hover:not(:disabled) {
  background-color: #dc2626;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.base-button--success {
  background-color: var(--color-success);
  color: #ffffff;
}

.base-button--success:hover:not(:disabled) {
  background-color: #059669;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* States */
.base-button:disabled,
.base-button--disabled,
.base-button--loading {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.base-button--full-width {
  width: 100%;
}

/* Icon */
.button-icon {
  width: 1.25em;
  height: 1.25em;
  flex-shrink: 0;
}

.button-icon-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.button-content {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
