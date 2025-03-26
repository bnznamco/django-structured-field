import { defineUserConfig } from 'vuepress'
import { defaultTheme } from '@vuepress/theme-default'
import { viteBundler } from '@vuepress/bundler-vite'
import { getSidebar } from './compose-sidenav'

export default defineUserConfig({
  lang: 'en-US',
  title: "Django Structured JSON Field",
  description: "Structured JSON Field for Django",
  base: '/django-structured-field/',
  bundler: viteBundler(),
  theme: defaultTheme({
    navbar: [
      { text: 'Home', link: '/' },
      { text: 'How to', link: '/Guide/How%20to/' },
    ],
    sidebar: getSidebar(),
    repo: 'bnznamco/django-structured-field',
    smoothScroll: true,
  }),
  head: [
    ['link', { rel: "icon", href: "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📑</text></svg>" }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css?family=Roboto:300,400,500,700|Material+Icons' }],
    ['link', { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/@mdi/font@4.x/css/materialdesignicons.min.css' }],
  ],
})
