import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [sveltekit()],
    server: {
        fs: {
            allow: ['..'] // This allows accessing files in parent directory
        }
    },
    optimizeDeps: {
        include: ['node:fs', 'node:path']
    }
});
