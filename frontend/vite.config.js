import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/recommend': 'http://localhost:8000',
      '/feedback':  'http://localhost:8000',
      '/ab-test':   'http://localhost:8000',
      '/embeddings':'http://localhost:8000',
      '/stats':     'http://localhost:8000',
    }
  }
})