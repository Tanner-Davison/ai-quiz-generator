import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, '.', '')
  
  return {
    plugins: [react()],
    
    // Environment-specific configuration
    define: {
      __APP_VERSION__: JSON.stringify('1.0.0'),
    },
    
    // Development server configuration
    server: {
      port: 3000,
      host: true,
      open: true,
      proxy: {
        // Proxy API calls to backend during development
        '/api': {
          target: env.VITE_API_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
    
    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom'],
          },
        },
      },
    },
    
    // Environment variables
    envPrefix: 'VITE_',
  }
})
