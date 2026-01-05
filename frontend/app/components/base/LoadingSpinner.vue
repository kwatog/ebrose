<template>
  <div
    role="status"
    :class="spinnerClasses"
    class="loading-spinner"
    :aria-label="label || 'Loading'"
  >
    <svg
      class="loading-spinner-svg"
      :class="`loading-spinner-svg--${color}`"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="loading-spinner-track"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="loading-spinner-path"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
    <span v-if="label" class="sr-only">{{ label }}</span>
    <span v-else class="sr-only">Loading</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  color?: 'primary' | 'white' | 'gray' | 'current'
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  color: 'primary'
})

const spinnerClasses = computed(() => [
  `loading-spinner--${props.size}`
])
</script>

<style scoped>
.loading-spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner-svg {
  animation: spin 1s linear infinite;
}

/* Sizes */
.loading-spinner--xs .loading-spinner-svg {
  width: 1rem;
  height: 1rem;
}

.loading-spinner--sm .loading-spinner-svg {
  width: 1.25rem;
  height: 1.25rem;
}

.loading-spinner--md .loading-spinner-svg {
  width: 1.5rem;
  height: 1.5rem;
}

.loading-spinner--lg .loading-spinner-svg {
  width: 2rem;
  height: 2rem;
}

.loading-spinner--xl .loading-spinner-svg {
  width: 3rem;
  height: 3rem;
}

/* Colors */
.loading-spinner-svg--primary {
  color: var(--color-primary);
}

.loading-spinner-svg--white {
  color: #ffffff;
}

.loading-spinner-svg--gray {
  color: var(--color-gray-400);
}

.loading-spinner-svg--current {
  color: currentColor;
}

.loading-spinner-track {
  opacity: 0.25;
}

.loading-spinner-path {
  opacity: 0.75;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
</style>
