import { execSync } from 'node:child_process'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const CLOUD_API = process.env.RISKLENS_API_URL ?? 'https://risklens-api-935079797801.europe-west1.run.app'
const TOKEN_LIFETIME_MS = 40 * 60 * 1000

let cached = { value: '', at: 0 }

// the cloud service is private, so the dev server adds your gcloud identity token to every call
function identityToken() {
  if (Date.now() - cached.at > TOKEN_LIFETIME_MS) {
    cached = { value: execSync('gcloud auth print-identity-token', { encoding: 'utf8' }).trim(), at: Date.now() }
  }
  return cached.value
}

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: CLOUD_API,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        timeout: 300000,
        proxyTimeout: 300000,
        configure: (proxy) => {
          proxy.on('proxyReq', (request) => {
            try {
              request.setHeader('Authorization', `Bearer ${identityToken()}`)
            } catch {
              console.error('Could not get a gcloud token. Run: gcloud auth login')
            }
          })
        },
      },
    },
  },
  test: { environment: 'node' },
})
