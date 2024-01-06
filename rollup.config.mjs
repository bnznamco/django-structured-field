import terser from '@rollup/plugin-terser';


export default {
    input: 'reative-forms/main.js',
    output: [
        {
            file: 'structured/static/js/structured-field-form.js',
            format: 'iife'
        },
        {
            file: 'structured/static/js/structured-field-form.min.js',
            format: 'iife',
            name: 'version',
            plugins: [terser()]
        }
    ]

};