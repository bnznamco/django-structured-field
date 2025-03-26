const sidebar = require('./compose-sidenav')

module.exports = {
  title: "Django Structured JSON Field",
  description: "Structured JSON Field for Django",
  theme: 'vuepress-theme-succinct',
  globalUIComponents: [
    'ThemeManager'
  ],
  base: '/django-structured-field/',
  themeConfig: {
    nextLinks: false,
    prevLinks: false,
    smoothScroll: true,
    repo: 'bnznamco/django-structured-field',
    nav: [
      { text: '🏠 Home', link: '/' },
      { text: '📚 How to', link: '/How%20To/' },
    ],
    sidebar: sidebar.getSidebar()
  },
  head: [
    ['link', { rel: "icon", href: "data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>📑</text></svg>" }],
    ['link', { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css?family=Roboto:300,400,500,700|Material+Icons' }],
    ['link', { rel: 'stylesheet', href: 'https://cdn.jsdelivr.net/npm/@mdi/font@4.x/css/materialdesignicons.min.css' }],
  ]
};
