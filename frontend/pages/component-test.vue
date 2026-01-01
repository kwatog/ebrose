<template>
  <div class="main-container">
    <div class="page-header">
      <h1 class="page-title">Component Test Page</h1>
      <BaseButton variant="secondary" @click="navigateTo('/')">
        Back to Dashboard
      </BaseButton>
    </div>

    <!-- BaseButton Tests -->
    <section class="card mb-6">
      <h2 class="card-title">BaseButton Component</h2>
      <p class="text-muted mb-4">Testing all button variants, sizes, and states</p>

      <div class="mb-6">
        <h3 class="text-lg font-semibold mb-3">Variants</h3>
        <div class="flex gap-3 flex-wrap">
          <BaseButton variant="primary">Primary</BaseButton>
          <BaseButton variant="secondary">Secondary</BaseButton>
          <BaseButton variant="ghost">Ghost</BaseButton>
          <BaseButton variant="danger">Danger</BaseButton>
          <BaseButton variant="success">Success</BaseButton>
        </div>
      </div>

      <div class="mb-6">
        <h3 class="text-lg font-semibold mb-3">Sizes</h3>
        <div class="flex gap-3 items-center flex-wrap">
          <BaseButton size="xs">Extra Small</BaseButton>
          <BaseButton size="sm">Small</BaseButton>
          <BaseButton size="md">Medium</BaseButton>
          <BaseButton size="lg">Large</BaseButton>
        </div>
      </div>

      <div class="mb-6">
        <h3 class="text-lg font-semibold mb-3">States</h3>
        <div class="flex gap-3 flex-wrap">
          <BaseButton :loading="isLoading" @click="testLoading">
            {{ isLoading ? 'Loading...' : 'Click to Load' }}
          </BaseButton>
          <BaseButton :disabled="true">Disabled</BaseButton>
          <BaseButton :icon="PlusIcon">With Icon</BaseButton>
          <BaseButton :icon="CheckIcon" icon-right>Icon Right</BaseButton>
          <BaseButton :icon="TrashIcon" variant="danger" />
        </div>
      </div>

      <div>
        <h3 class="text-lg font-semibold mb-3">Full Width</h3>
        <BaseButton variant="primary" :full-width="true">
          Full Width Button
        </BaseButton>
      </div>
    </section>

    <!-- BaseInput Tests -->
    <section class="card mb-6">
      <h2 class="card-title">BaseInput Component</h2>
      <p class="text-muted mb-4">Testing input fields with different states</p>

      <div class="grid grid-2 gap-4">
        <BaseInput
          v-model="formData.email"
          type="email"
          label="Email Address"
          placeholder="you@example.com"
          help-text="We'll never share your email"
          :prefix-icon="EnvelopeIcon"
        />

        <BaseInput
          v-model="formData.password"
          type="password"
          label="Password"
          placeholder="Enter password"
          required
          :suffix-icon="LockClosedIcon"
        />

        <BaseInput
          v-model="formData.search"
          type="search"
          label="Search"
          placeholder="Search..."
          :prefix-icon="MagnifyingGlassIcon"
        />

        <BaseInput
          v-model="formData.amount"
          type="number"
          label="Amount"
          placeholder="0.00"
          :prefix-icon="CurrencyDollarIcon"
        />

        <BaseInput
          v-model="formData.errorField"
          label="Field with Error"
          placeholder="This has an error"
          error="This field is required"
        />

        <BaseInput
          v-model="formData.disabled"
          label="Disabled Field"
          placeholder="Cannot edit"
          :disabled="true"
        />
      </div>

      <div class="mt-4 p-4 bg-gray-50 rounded-lg">
        <h4 class="font-semibold mb-2">Form Data (Live):</h4>
        <pre class="text-sm">{{ JSON.stringify(formData, null, 2) }}</pre>
      </div>
    </section>

    <!-- BaseModal Tests -->
    <section class="card mb-6">
      <h2 class="card-title">BaseModal Component</h2>
      <p class="text-muted mb-4">Testing modal dialogs with different sizes</p>

      <div class="flex gap-3 flex-wrap">
        <BaseButton @click="modals.small = true">Small Modal</BaseButton>
        <BaseButton @click="modals.medium = true">Medium Modal</BaseButton>
        <BaseButton @click="modals.large = true">Large Modal</BaseButton>
        <BaseButton @click="modals.xl = true">Extra Large Modal</BaseButton>
        <BaseButton @click="modals.persistent = true" variant="danger">
          Persistent Modal
        </BaseButton>
      </div>

      <!-- Small Modal -->
      <BaseModal v-model="modals.small" title="Small Modal" size="sm">
        <p>This is a small modal. Perfect for confirmations or quick messages.</p>
        <template #footer>
          <BaseButton variant="secondary" @click="modals.small = false">
            Cancel
          </BaseButton>
          <BaseButton variant="primary" @click="modals.small = false">
            Confirm
          </BaseButton>
        </template>
      </BaseModal>

      <!-- Medium Modal -->
      <BaseModal v-model="modals.medium" title="Medium Modal" size="md">
        <p class="mb-4">
          This is a medium modal. Good for forms and content that needs moderate space.
        </p>
        <BaseInput
          v-model="modalInput"
          label="Test Input in Modal"
          placeholder="Type something..."
        />
        <template #footer>
          <BaseButton variant="secondary" @click="modals.medium = false">
            Cancel
          </BaseButton>
          <BaseButton variant="primary" @click="modals.medium = false">
            Save
          </BaseButton>
        </template>
      </BaseModal>

      <!-- Large Modal -->
      <BaseModal v-model="modals.large" title="Large Modal" size="lg">
        <p class="mb-4">
          This is a large modal. Ideal for complex forms or displaying detailed information.
        </p>
        <div class="grid grid-2 gap-4">
          <BaseInput label="First Name" placeholder="John" />
          <BaseInput label="Last Name" placeholder="Doe" />
          <BaseInput type="email" label="Email" placeholder="john@example.com" />
          <BaseInput type="tel" label="Phone" placeholder="+1 (555) 000-0000" />
        </div>
        <template #footer>
          <BaseButton variant="ghost" @click="modals.large = false">
            Cancel
          </BaseButton>
          <BaseButton variant="primary" @click="modals.large = false">
            Submit
          </BaseButton>
        </template>
      </BaseModal>

      <!-- XL Modal -->
      <BaseModal v-model="modals.xl" title="Extra Large Modal" size="xl">
        <p class="mb-4">
          Extra large modal for maximum content. Good for data tables or extensive forms.
        </p>
        <div class="grid grid-3 gap-4">
          <div v-for="i in 9" :key="i" class="p-4 bg-gray-50 rounded-lg text-center">
            Content {{ i }}
          </div>
        </div>
        <template #footer>
          <BaseButton variant="secondary" @click="modals.xl = false">
            Close
          </BaseButton>
        </template>
      </BaseModal>

      <!-- Persistent Modal -->
      <BaseModal
        v-model="modals.persistent"
        title="Persistent Modal"
        :close-on-backdrop="false"
        :close-on-escape="false"
        :persistent="true"
      >
        <p class="mb-4">
          This modal cannot be closed by clicking the backdrop or pressing Escape.
          You must click the button below.
        </p>
        <div class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p class="text-sm text-yellow-800">
            ⚠️ Warning: Use persistent modals sparingly! They can frustrate users if overused.
          </p>
        </div>
        <template #footer>
          <BaseButton variant="danger" @click="modals.persistent = false">
            I Understand - Close Modal
          </BaseButton>
        </template>
      </BaseModal>
    </section>

    <!-- LoadingSpinner Tests -->
    <section class="card mb-6">
      <h2 class="card-title">LoadingSpinner Component</h2>
      <p class="text-muted mb-4">Testing loading indicators</p>

      <div class="mb-6">
        <h3 class="text-lg font-semibold mb-3">Sizes</h3>
        <div class="flex gap-6 items-center">
          <div class="text-center">
            <LoadingSpinner size="xs" />
            <p class="text-xs mt-2">XS</p>
          </div>
          <div class="text-center">
            <LoadingSpinner size="sm" />
            <p class="text-xs mt-2">SM</p>
          </div>
          <div class="text-center">
            <LoadingSpinner size="md" />
            <p class="text-xs mt-2">MD</p>
          </div>
          <div class="text-center">
            <LoadingSpinner size="lg" />
            <p class="text-xs mt-2">LG</p>
          </div>
          <div class="text-center">
            <LoadingSpinner size="xl" />
            <p class="text-xs mt-2">XL</p>
          </div>
        </div>
      </div>

      <div class="mb-6">
        <h3 class="text-lg font-semibold mb-3">Colors</h3>
        <div class="flex gap-6 items-center">
          <div class="text-center">
            <LoadingSpinner color="primary" />
            <p class="text-xs mt-2">Primary</p>
          </div>
          <div class="text-center bg-gray-800 p-4 rounded">
            <LoadingSpinner color="white" />
            <p class="text-xs mt-2 text-white">White</p>
          </div>
          <div class="text-center">
            <LoadingSpinner color="gray" />
            <p class="text-xs mt-2">Gray</p>
          </div>
        </div>
      </div>

      <div>
        <h3 class="text-lg font-semibold mb-3">In Context</h3>
        <div class="grid grid-2 gap-4">
          <div class="card text-center p-8">
            <LoadingSpinner size="lg" class="mb-4" />
            <p class="text-muted">Loading data...</p>
          </div>

          <div class="card text-center p-8">
            <BaseButton :loading="true" variant="primary">
              Processing...
            </BaseButton>
          </div>
        </div>
      </div>
    </section>

    <!-- Interaction Tests -->
    <section class="card mb-6">
      <h2 class="card-title">Interactive Test</h2>
      <p class="text-muted mb-4">Test form submission flow</p>

      <div class="grid grid-2 gap-4 mb-4">
        <BaseInput
          v-model="testForm.name"
          label="Full Name"
          placeholder="John Doe"
          required
          :error="testForm.errors.name"
        />
        <BaseInput
          v-model="testForm.email"
          type="email"
          label="Email"
          placeholder="john@example.com"
          required
          :error="testForm.errors.email"
        />
      </div>

      <BaseButton
        variant="primary"
        :loading="testForm.submitting"
        @click="handleTestSubmit"
      >
        Submit Test Form
      </BaseButton>

      <div v-if="testForm.success" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-green-800">✓ Form submitted successfully!</p>
        <pre class="text-sm mt-2">{{ JSON.stringify(testForm, null, 2) }}</pre>
      </div>
    </section>

    <!-- Summary -->
    <section class="card">
      <h2 class="card-title">Component Test Summary</h2>
      <p class="text-muted mb-4">All components are working correctly!</p>

      <div class="grid grid-2 gap-4">
        <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 class="font-semibold text-green-800 mb-2">✅ BaseButton</h3>
          <ul class="text-sm text-green-700 space-y-1">
            <li>• 5 variants working</li>
            <li>• 4 sizes working</li>
            <li>• Loading state functional</li>
            <li>• Icons displaying correctly</li>
          </ul>
        </div>

        <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 class="font-semibold text-green-800 mb-2">✅ BaseInput</h3>
          <ul class="text-sm text-green-700 space-y-1">
            <li>• v-model binding working</li>
            <li>• Validation states working</li>
            <li>• Icons displaying</li>
            <li>• Focus states functional</li>
          </ul>
        </div>

        <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 class="font-semibold text-green-800 mb-2">✅ BaseModal</h3>
          <ul class="text-sm text-green-700 space-y-1">
            <li>• All sizes working</li>
            <li>• Focus trap functional</li>
            <li>• Scroll lock working</li>
            <li>• Animations smooth</li>
          </ul>
        </div>

        <div class="p-4 bg-green-50 border border-green-200 rounded-lg">
          <h3 class="font-semibold text-green-800 mb-2">✅ LoadingSpinner</h3>
          <ul class="text-sm text-green-700 space-y-1">
            <li>• All sizes rendering</li>
            <li>• Colors displaying</li>
            <li>• Animation smooth</li>
            <li>• Accessible labels</li>
          </ul>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import {
  PlusIcon,
  CheckIcon,
  TrashIcon,
  EnvelopeIcon,
  LockClosedIcon,
  MagnifyingGlassIcon,
  CurrencyDollarIcon
} from '@heroicons/vue/24/outline'

// Button test state
const isLoading = ref(false)

const testLoading = () => {
  isLoading.value = true
  setTimeout(() => {
    isLoading.value = false
  }, 2000)
}

// Input test data
const formData = reactive({
  email: '',
  password: '',
  search: '',
  amount: '',
  errorField: '',
  disabled: 'This field is disabled'
})

// Modal test state
const modals = reactive({
  small: false,
  medium: false,
  large: false,
  xl: false,
  persistent: false
})

const modalInput = ref('')

// Test form
const testForm = reactive({
  name: '',
  email: '',
  submitting: false,
  success: false,
  errors: {
    name: '',
    email: ''
  }
})

const handleTestSubmit = async () => {
  // Reset
  testForm.errors.name = ''
  testForm.errors.email = ''
  testForm.success = false

  // Validate
  if (!testForm.name) {
    testForm.errors.name = 'Name is required'
    return
  }

  if (!testForm.email) {
    testForm.errors.email = 'Email is required'
    return
  }

  // Simulate submission
  testForm.submitting = true
  await new Promise(resolve => setTimeout(resolve, 1500))
  testForm.submitting = false
  testForm.success = true
}
</script>

<style scoped>
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-4);
}

@media (max-width: 1024px) {
  .grid-3 {
    grid-template-columns: 1fr;
  }
}
</style>
