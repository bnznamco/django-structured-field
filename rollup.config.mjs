import terser from '@rollup/plugin-terser';
import scss from 'rollup-plugin-scss'


export default {
    input: 'reactive-forms/main.js',
    output: [
        {
            format: 'iife',
            dir: 'structured/static',
            sourcemap: true,
            assetFileNames: 'css/structured-field-form.min.css',
            entryFileNames: 'js/structured-field-form.js'
        },
        {
            dir: 'structured/static',
            entryFileNames: 'js/structured-field-form.min.js',
            assetFileNames: 'css/structured-field-form.min.css',
            format: 'iife',
            plugins: [terser()]
        }
    ],
    plugins: [scss({ outputStyle: 'compressed', watch: 'reactive-forms/scss/components' })]

};