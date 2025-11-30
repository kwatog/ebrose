export default defineNuxtConfig({
  devtools: { enabled: false }, // Disable devtools in production
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
  // Fix CSP issues for production deployment
  nitro: {
    experimental: {
      wasm: false
    }
  },
  // Disable source maps to avoid CSP eval issues
  sourcemap: {
    server: false,
    client: false
  },
  compatibilityDate: '2024-11-01'
})
