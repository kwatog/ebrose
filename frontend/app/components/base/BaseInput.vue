<template>
  <div class="base-input-wrapper">
    <label
      v-if="label"
      :for="inputId"
      class="base-input-label"
    >
      {{ label }}
      <span v-if="required" class="base-input-required" aria-label="required">*</span>
    </label>

    <div class="base-input-container" :class="containerClasses">
      <component
        v-if="prefixIcon"
        :is="prefixIcon"
        class="base-input-prefix-icon"
        aria-hidden="true"
      />

      <slot name="prefix" />

      <input
        :id="inputId"
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :maxlength="maxlength"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${inputId}-error` : helpText ? `${inputId}-help` : undefined"
        class="base-input"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
      />

      <slot name="suffix" />

      <component
        v-if="suffixIcon"
        :is="suffixIcon"
        class="base-input-suffix-icon"
        aria-hidden="true"
      />
    </div>

    <p
      v-if="error"
      :id="`${inputId}-error`"
      class="base-input-error"
    >
      {{ error }}
    </p>

    <p
      v-else-if="helpText"
      :id="`${inputId}-help`"
      class="base-input-help"
    >
      {{ helpText }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, type Component } from 'vue'

interface Props {
  modelValue: string | number
  type?: 'text' | 'email' | 'number' | 'password' | 'date' | 'search' | 'tel' | 'url'
  label?: string
  placeholder?: string
  helpText?: string
  error?: string
  disabled?: boolean
  required?: boolean
  prefixIcon?: Component
  suffixIcon?: Component
  maxlength?: number
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  required: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  'focus': [event: FocusEvent]
  'blur': [event: FocusEvent]
  'input': [event: Event]
}>()

const inputRef = ref<HTMLInputElement>()
const isFocused = ref(false)

const inputId = computed(() => props.id || `input-${Math.random().toString(36).substr(2, 9)}`)

const containerClasses = computed(() => ({
  'base-input-container--focused': isFocused.value,
  'base-input-container--error': !!props.error,
  'base-input-container--disabled': props.disabled
}))

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  let value: string | number = target.value

  if (props.type === 'number') {
    value = target.valueAsNumber || 0
  }

  emit('update:modelValue', value)
  emit('input', event)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

// Expose methods for parent components
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur()
})
</script>

<style scoped>
.base-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.base-input-label {
  display: block;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text);
}

.base-input-required {
  color: var(--color-error);
  margin-left: var(--spacing-1);
}

.base-input-container {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  background-color: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--spacing-3);
  transition: all var(--transition-fast);
}

.base-input-container:hover:not(.base-input-container--disabled) {
  border-color: var(--color-gray-300);
}

.base-input-container--focused {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 215, 96, 0.1);
}

.base-input-container--error {
  border-color: var(--color-error);
}

.base-input-container--error.base-input-container--focused {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.base-input-container--disabled {
  background-color: var(--color-gray-50);
  cursor: not-allowed;
  opacity: 0.6;
}

.base-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: var(--text-base);
  font-family: inherit;
  color: var(--color-text);
  min-width: 0;
}

.base-input::placeholder {
  color: var(--color-text-muted);
}

.base-input:disabled {
  cursor: not-allowed;
}

/* Remove number input spinners */
.base-input[type="number"]::-webkit-inner-spin-button,
.base-input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.base-input[type="number"] {
  -moz-appearance: textfield;
}

.base-input-prefix-icon,
.base-input-suffix-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  color: var(--color-gray-400);
}

.base-input-container--focused .base-input-prefix-icon,
.base-input-container--focused .base-input-suffix-icon {
  color: var(--color-primary);
}

.base-input-error {
  color: var(--color-error);
  font-size: var(--text-sm);
  margin: 0;
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
}

.base-input-help {
  color: var(--color-text-light);
  font-size: var(--text-sm);
  margin: 0;
}
</style>
