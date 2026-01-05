<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
  helpText?: string
  error?: string
  disabled?: boolean
  required?: boolean
  rows?: number
  maxlength?: number
  autoResize?: boolean
  showCount?: boolean
}>(), {
  placeholder: '',
  rows: 4,
  disabled: false,
  required: false,
  autoResize: false,
  showCount: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  focus: []
  blur: []
  input: []
}>()

const textarea = ref<HTMLTextAreaElement | null>(null)

const characterCount = computed(() => {
  if (!props.maxlength) return null
  return `${(props.modelValue || '').length}/${props.maxlength}`
})

const onInput = (event: Event) => {
  const target = event.target as HTMLTextAreaElement
  emit('update:modelValue', target.value)
  emit('input')
  
  if (props.autoResize && textarea.value) {
    textarea.value.style.height = 'auto'
    textarea.value.style.height = `${textarea.value.scrollHeight}px`
  }
}
</script>

<template>
  <div class="base-textarea-wrapper">
    <label v-if="label" class="base-textarea-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <textarea
      ref="textarea"
      :value="modelValue"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="maxlength"
      :rows="rows"
      class="base-textarea"
      :class="{ 'is-error': error }"
      @input="onInput"
      @focus="emit('focus')"
      @blur="emit('blur')"
    />
    
    <div class="textarea-footer">
      <p v-if="error" class="base-textarea-error">{{ error }}</p>
      <p v-else-if="helpText" class="base-textarea-help">{{ helpText }}</p>
      <span v-if="showCount && characterCount" class="textarea-count">{{ characterCount }}</span>
    </div>
  </div>
</template>

<style scoped>
.base-textarea-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.base-textarea-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-gray-700);
}

.required {
  color: var(--color-error);
}

.base-textarea {
  width: 100%;
  padding: var(--spacing-3);
  border: 1px solid var(--color-gray-300);
  border-radius: var(--radius-lg);
  font-size: var(--text-base);
  font-family: inherit;
  resize: vertical;
  transition: all var(--transition-fast);
  background: white;
}

.base-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(30, 215, 96, 0.1);
}

.base-textarea:disabled {
  background: var(--color-gray-100);
  cursor: not-allowed;
  opacity: 0.7;
}

.base-textarea.is-error {
  border-color: var(--color-error);
}

.base-textarea.is-error:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.base-textarea-error {
  font-size: var(--text-sm);
  color: var(--color-error);
}

.base-textarea-help {
  font-size: var(--text-sm);
  color: var(--color-gray-500);
}

.textarea-count {
  font-size: var(--text-xs);
  color: var(--color-gray-400);
}
</style>
