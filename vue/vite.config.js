import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue2'

// https://vitejs.dev/config/
const path = require("path");

export default defineConfig({
    // Run dev on :8080
    server: {
        port: 8080
    }, // Vue Plugin
    plugins: [vue()], // Path
    resolve: {
        alias: {
            "@": path.resolve(__dirname, "./src"),
        },
    }, // Dist dir
    build: {
        outDir: '../web', emptyOutDir: true, // also necessary
    }
})