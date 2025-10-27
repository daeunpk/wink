import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // 프론트 개발 서버
    proxy: {
      '/api': {
        target: 'http://localhost:8080', // Spring Boot 백엔드
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/ai': {
        target: 'http://localhost:8000', // Python AI 서버
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai/, ''),
      },
    },
  },
})
