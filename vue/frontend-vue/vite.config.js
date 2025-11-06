import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
    optimizeDeps: {
    exclude: ['vue-plotly'] // Evita prebundling de vue-plotly
  },
  server: {
    port: 8081,              // 👈 mismo puerto que usabas con Vue CLI
    host: 'localhost',       // accesible desde localhost
    open: true               // abre el navegador automáticamente
  },
  build: {
    outDir: 'dist',          // carpeta de salida del build
    sourcemap: true,         // útil para debug
  },
  css: {
    preprocessorOptions: {
      scss: {
        // Inyecta SÓLO la paleta de colores, no los estilos
        additionalData: `@use "@/assets/scss/_variables.scss" as *;`
      }
    }
  },
  base: '/',                 // ruta base (importante para router con history)
})
