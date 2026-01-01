<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="modelValue"
        class="base-modal-overlay"
        :class="overlayClasses"
        @click="handleBackdropClick"
        @keydown.esc="handleEscape"
      >
        <Transition name="modal-slide">
          <div
            v-if="modelValue"
            ref="modalRef"
            role="dialog"
            aria-modal="true"
            :aria-labelledby="title ? 'modal-title' : undefined"
            :class="modalClasses"
            class="base-modal"
            @click.stop
          >
            <!-- Header -->
            <div v-if="$slots.header || title || showClose" class="base-modal-header">
              <slot name="header">
                <h2 v-if="title" id="modal-title" class="base-modal-title">
                  {{ title }}
                </h2>
              </slot>

              <button
                v-if="showClose"
                type="button"
                class="base-modal-close"
                aria-label="Close modal"
                @click="handleClose"
              >
                <XMarkIcon class="base-modal-close-icon" aria-hidden="true" />
              </button>
            </div>

            <!-- Body -->
            <div class="base-modal-body">
              <slot />
            </div>

            <!-- Footer -->
            <div v-if="$slots.footer" class="base-modal-footer">
              <slot name="footer" />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

interface Props {
  modelValue: boolean
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  title?: string
  closeOnBackdrop?: boolean
  closeOnEscape?: boolean
  showClose?: boolean
  persistent?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
  closeOnBackdrop: true,
  closeOnEscape: true,
  showClose: true,
  persistent: false
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'close': []
  'open': []
}>()

const modalRef = ref<HTMLDivElement>()
const previousActiveElement = ref<HTMLElement | null>(null)

const modalClasses = computed(() => [
  `base-modal--${props.size}`
])

const overlayClasses = computed(() => ({
  'base-modal-overlay--persistent': props.persistent
}))

const handleClose = () => {
  if (!props.persistent) {
    emit('update:modelValue', false)
    emit('close')
  }
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    handleClose()
  }
}

const handleEscape = () => {
  if (props.closeOnEscape) {
    handleClose()
  }
}

// Focus management
const trapFocus = (event: KeyboardEvent) => {
  if (!modalRef.value || event.key !== 'Tab') return

  const focusableElements = modalRef.value.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )
  const firstFocusable = focusableElements[0] as HTMLElement
  const lastFocusable = focusableElements[focusableElements.length - 1] as HTMLElement

  if (event.shiftKey) {
    if (document.activeElement === firstFocusable) {
      lastFocusable?.focus()
      event.preventDefault()
    }
  } else {
    if (document.activeElement === lastFocusable) {
      firstFocusable?.focus()
      event.preventDefault()
    }
  }
}

// Body scroll lock
const lockBodyScroll = () => {
  const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth
  document.body.style.overflow = 'hidden'
  document.body.style.paddingRight = `${scrollbarWidth}px`
}

const unlockBodyScroll = () => {
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
}

// Watch for modal open/close
watch(() => props.modelValue, async (newValue) => {
  if (newValue) {
    previousActiveElement.value = document.activeElement as HTMLElement
    lockBodyScroll()
    emit('open')

    // Focus first focusable element
    await nextTick()
    const focusableElements = modalRef.value?.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )
    if (focusableElements && focusableElements.length > 0) {
      (focusableElements[0] as HTMLElement).focus()
    }
  } else {
    unlockBodyScroll()
    // Restore focus to previous element
    if (previousActiveElement.value) {
      previousActiveElement.value.focus()
      previousActiveElement.value = null
    }
  }
})

// Event listeners
onMounted(() => {
  document.addEventListener('keydown', trapFocus)
})

onUnmounted(() => {
  document.removeEventListener('keydown', trapFocus)
  unlockBodyScroll()
})
</script>

<style scoped>
.base-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-modal-backdrop);
  padding: var(--spacing-4);
  overflow-y: auto;
}

.base-modal {
  background-color: var(--color-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: 100%;
  max-height: calc(100vh - var(--spacing-8));
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: var(--z-modal);
}

/* Sizes */
.base-modal--sm {
  max-width: 400px;
}

.base-modal--md {
  max-width: 600px;
}

.base-modal--lg {
  max-width: 800px;
}

.base-modal--xl {
  max-width: 1200px;
}

.base-modal--full {
  max-width: 100%;
  max-height: 100vh;
  height: 100%;
  border-radius: 0;
}

.base-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-6);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.base-modal-title {
  font-size: var(--text-2xl);
  font-weight: var(--font-semibold);
  margin: 0;
  color: var(--color-text);
}

.base-modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  color: var(--color-gray-500);
  transition: all var(--transition-fast);
  margin-left: var(--spacing-4);
}

.base-modal-close:hover {
  background-color: var(--color-gray-100);
  color: var(--color-gray-700);
}

.base-modal-close:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.base-modal-close-icon {
  width: 1.5rem;
  height: 1.5rem;
}

.base-modal-body {
  padding: var(--spacing-6);
  overflow-y: auto;
  flex: 1;
}

.base-modal-footer {
  padding: var(--spacing-6);
  border-top: 1px solid var(--color-border);
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-3);
  flex-shrink: 0;
}

/* Animations */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity var(--transition-base);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-slide-enter-active,
.modal-slide-leave-active {
  transition: all var(--transition-slow);
}

.modal-slide-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}

.modal-slide-leave-to {
  transform: translateY(20px);
  opacity: 0;
}

/* Responsive */
@media (max-width: 640px) {
  .base-modal-overlay {
    padding: 0;
  }

  .base-modal {
    max-height: 100vh;
    border-radius: 0;
  }

  .base-modal--sm,
  .base-modal--md,
  .base-modal--lg,
  .base-modal--xl {
    max-width: 100%;
  }

  .base-modal-header,
  .base-modal-body,
  .base-modal-footer {
    padding: var(--spacing-4);
  }
}
</style>
