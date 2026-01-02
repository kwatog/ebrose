<script setup lang="ts">
interface Props {
  modelValue: string
  showRequirements?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showRequirements: true
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const password = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const requirements = computed(() => [
  { label: 'At least 8 characters', met: password.value.length >= 8 },
  { label: 'One uppercase letter', met: /[A-Z]/.test(password.value) },
  { label: 'One lowercase letter', met: /[a-z]/.test(password.value) },
  { label: 'One digit', met: /[0-9]/.test(password.value) },
  { label: 'One special character', met: /[!@#$%^&*(),.?":{}|<>]/.test(password.value) }
])

const strength = computed(() => {
  const metCount = requirements.value.filter(r => r.met).length
  if (metCount === 0) return { level: 0, label: '', color: '' }
  if (metCount <= 2) return { level: 1, label: 'Weak', color: '#ef4444' }
  if (metCount <= 3) return { level: 2, label: 'Fair', color: '#f59e0b' }
  if (metCount <= 4) return { level: 3, label: 'Good', color: '#3b82f6' }
  return { level: 4, label: 'Strong', color: '#22c55e' }
})

const strengthWidth = computed(() => (strength.value.level / 4) * 100)
</script>

<template>
  <div class="password-strength">
    <BaseInput
      :model-value="password"
      @update:model-value="password = $event"
      type="password"
      label="Password"
      placeholder="Enter password"
      required
    />

    <div v-if="password.length > 0" class="strength-indicator">
      <div class="strength-bar">
        <div 
          class="strength-fill" 
          :style="{ width: strengthWidth + '%', backgroundColor: strength.color }"
        />
      </div>
      <span class="strength-label" :style="{ color: strength.color }">
        {{ strength.label }}
      </span>
    </div>

    <ul v-if="showRequirements && password.length > 0" class="requirements">
      <li 
        v-for="req in requirements" 
        :key="req.label"
        :class="{ met: req.met }"
      >
        <svg v-if="req.met" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="check-icon">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="x-icon">
          <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
        {{ req.label }}
      </li>
    </ul>
  </div>
</template>

<style scoped>
.password-strength {
  width: 100%;
}

.strength-indicator {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.strength-bar {
  flex: 1;
  height: 6px;
  background-color: #e5e7eb;
  border-radius: 3px;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.strength-label {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 50px;
}

.requirements {
  list-style: none;
  padding: 0;
  margin: 0.75rem 0 0 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.requirements li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #6b7280;
  transition: color 0.2s ease;
}

.requirements li.met {
  color: #22c55e;
}

.check-icon, .x-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

.check-icon {
  color: #22c55e;
}

.x-icon {
  color: #9ca3af;
}
</style>
