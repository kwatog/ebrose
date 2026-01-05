<script setup lang="ts">
withDefaults(defineProps<{
  placement?: 'bottom-start' | 'bottom-end' | 'top-start' | 'top-end'
  disabled?: boolean
  closeOnClick?: boolean
}>(), {
  placement: 'bottom-start',
  disabled: false,
  closeOnClick: true
})

const emit = defineEmits<{
  open: []
  close: []
}>()

const isOpen = ref(false)
const dropdownRef = ref<HTMLElement | null>(null)

const toggle = () => {
  if (props.disabled) return
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    emit('open')
  } else {
    emit('close')
  }
}

const close = () => {
  isOpen.value = false
  emit('close')
}

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    close()
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="dropdownRef" class="base-dropdown" :class="{ 'is-open': isOpen }">
    <div class="dropdown-trigger" @click="toggle">
      <slot name="trigger">
        <button class="dropdown-default-trigger">Dropdown ▼</button>
      </slot>
    </div>
    
    <Transition name="dropdown">
      <div 
        v-if="isOpen" 
        class="dropdown-menu"
        :class="[`dropdown-${placement}`]"
      >
        <div class="dropdown-content" @click="closeOnClick && close()">
          <slot />
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.base-dropdown {
  position: relative;
  display: inline-block;
}

.dropdown-trigger {
  cursor: pointer;
}

.dropdown-default-trigger {
  background: white;
  border: 1px solid var(--color-gray-300);
  padding: var(--spacing-2) var(--spacing-4);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dropdown-default-trigger:hover {
  border-color: var(--color-gray-400);
  background: var(--color-gray-50);
}

.dropdown-menu {
  position: absolute;
  z-index: var(--z-dropdown);
  min-width: 200px;
  margin-top: var(--spacing-2);
}

.dropdown-bottom-start {
  left: 0;
}

.dropdown-bottom-end {
  right: 0;
}

.dropdown-top-start {
  bottom: 100%;
  left: 0;
  margin-bottom: var(--spacing-2);
  margin-top: 0;
}

.dropdown-top-end {
  bottom: 100%;
  right: 0;
  margin-bottom: var(--spacing-2);
  margin-top: 0;
}

.dropdown-content {
  background: white;
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-gray-200);
  padding: var(--spacing-2);
}

.dropdown-content > :deep(*) {
  display: block;
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--color-gray-700);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.dropdown-content > :deep(*:hover) {
  background: var(--color-gray-100);
  color: var(--color-gray-900);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.dropdown-enter-from.dropdown-top-start,
.dropdown-enter-from.dropdown-top-end,
.dropdown-leave-to.dropdown-top-start,
.dropdown-leave-to.dropdown-top-end {
  transform: translateY(8px);
}
</style>
