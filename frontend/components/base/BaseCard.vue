<script setup lang="ts">
const props = withDefaults(defineProps<{
  title?: string
  subtitle?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hoverable?: boolean
  clickable?: boolean
}>(), {
  padding: 'md',
  hoverable: false,
  clickable: false
})

const emit = defineEmits<{
  click: []
}>()

const paddingClasses = {
  none: 'card-padding-none',
  sm: 'card-padding-sm',
  md: 'card-padding-md',
  lg: 'card-padding-lg'
}
</script>

<template>
  <div 
    class="base-card" 
    :class="[paddingClasses[padding], { 'card-hoverable': hoverable, 'card-clickable': clickable }]"
    @click="clickable && emit('click')"
  >
    <div v-if="title || subtitle || $slots.header" class="card-header">
      <slot name="header">
        <h3 v-if="title" class="card-title">{{ title }}</h3>
        <p v-if="subtitle" class="card-subtitle">{{ subtitle }}</p>
      </slot>
    </div>
    
    <div class="card-body">
      <slot />
    </div>
    
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer" />
    </div>
  </div>
</template>

<style scoped>
.base-card {
  background: white;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-gray-100);
}

.card-hoverable {
  transition: all var(--transition-base);
}

.card-hoverable:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.card-clickable {
  cursor: pointer;
}

.card-padding-none .card-body {
  padding: 0;
}

.card-padding-sm .card-body {
  padding: var(--spacing-2);
}

.card-padding-md .card-body {
  padding: var(--spacing-4);
}

.card-padding-lg .card-body {
  padding: var(--spacing-6);
}

.card-header {
  padding: var(--spacing-4) var(--spacing-4) 0;
}

.card-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-gray-900);
  margin: 0;
}

.card-subtitle {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
  margin: var(--spacing-1) 0 0;
}

.card-footer {
  padding: var(--spacing-4);
  border-top: 1px solid var(--color-gray-100);
  margin-top: var(--spacing-4);
}
</style>
