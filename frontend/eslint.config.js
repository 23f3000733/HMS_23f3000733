import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'

export default [
    js.configs.recommended,
    ...pluginVue.configs['flat/recommended'],
    {
        files: ['**/*.vue', '**/*.js'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',
            globals: {
                // Browser globals
                window: 'readonly',
                document: 'readonly',
                console: 'readonly',
                alert: 'readonly',
                confirm: 'readonly',
                localStorage: 'readonly',
                // Node globals
                process: 'readonly',
                __dirname: 'readonly',
                // Vite
                import: 'readonly'
            }
        },
        rules: {
            // Vue 3 Composition API
            'vue/multi-word-component-names': 'off',
            'vue/no-unused-vars': 'error',
            'vue/no-unused-components': 'warn',

            // General
            'no-unused-vars': ['error', { varsIgnorePattern: '^_', argsIgnorePattern: '^_' }],
            'no-console': ['warn', { allow: ['warn', 'error'] }],
            'no-debugger': 'warn',

            // Code quality
            'prefer-const': 'error',
            'no-var': 'error',
            'object-shorthand': 'warn',
            'prefer-template': 'warn',

            // Import/Export
            'no-duplicate-imports': 'error'
        }
    },
    {
        ignores: ['dist/**', 'node_modules/**', '*.config.js']
    }
]
