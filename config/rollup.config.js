import svelte from 'rollup-plugin-svelte';
import resolve from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import css from 'rollup-plugin-css-only';

export default {
    input: 'webserver/website/static/js/app.js',
    output: {
        file: 'webserver/website/static/js/bundle.js',
        format: 'iife',
        name: 'app'
    },
    plugins: [
        svelte({
            compilerOptions: {
                dev: true
            },
            emitCss: true
        }),
        css({
            output: 'bundle.css'
        }),
        resolve({
            browser: true,
            dedupe: ['svelte']
        }),
        commonjs()
    ]
}; 