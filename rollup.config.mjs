import { nodeResolve } from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import json from '@rollup/plugin-json';
import replace from 'rollup-plugin-replace';
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
    ],
    plugins: [
        nodeResolve(), json(),
        commonjs({ transformMixedEsModules: true }),
        replace({
            'process.env.NODE_ENV': JSON.stringify('production'),
            '__VUE_PROD_DEVTOOLS__': JSON.stringify(false)
        }),
    ]

};