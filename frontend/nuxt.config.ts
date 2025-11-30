export default defineNuxtConfig({
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'Mazarbul',
      meta: [
        { name: 'description', content: 'Mazarbul - Chamber of Spend Records' }
      ]
    }
  },
  runtimeConfig: {
    // Private config (SSR only) - defaults to internal Docker URL
    apiBase: process.env.NUXT_API_BASE || 'http://localhost:8000',
    public: {
      // Public config (Client-side) - defaults to browser-accessible URL
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000'
    }
  },
  compatibilityDate: '2024-11-01'
})
