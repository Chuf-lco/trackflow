export default defineConfig({
  // ... other config
  server: {
    proxy: {
      '/api': {
        target: 'https://trackflow-backend-2mxx.onrender.com',
        changeOrigin: true,
      }
    }
  }
})