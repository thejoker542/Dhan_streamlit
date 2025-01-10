import adapter from '@sveltejs/adapter-auto';
import preprocess from 'svelte-preprocess'; // Changed this line

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: preprocess(),  // Changed this line

	kit: {
		adapter: adapter(),
		files: {
			lib: 'src/lib'
		},
		alias: {
			$lib: './src/lib'
		}
	}
};

export default config;
