import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'ERDI Docs',
  tagline: 'Integration guide for ERDI laser rangefinder modules',
  favicon: 'img/favicon.svg',

  future: {
    v4: true,
  },

  url: 'https://erdilrf.com',
  baseUrl: '/docs/',
  trailingSlash: true,

  organizationName: 'ErdiTech',
  projectName: 'erdi-docs',

  onBrokenLinks: 'throw',
  onBrokenAnchors: 'warn',
  markdown: {
    format: 'detect',
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  headTags: [
    {
      tagName: 'script',
      attributes: {type: 'application/ld+json'},
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: 'ERDI Docs',
        url: 'https://erdilrf.com/docs/',
        publisher: {'@type': 'Organization', name: 'ERDI TECH LTD', url: 'https://erdilrf.com/'},
      }),
    },
  ],

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: './sidebars.ts',
          editUrl: 'https://github.com/ErdiTech/erdi-docs/edit/main/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
        sitemap: {
          changefreq: 'weekly',
          priority: 0.6,
          filename: 'sitemap.xml',
          ignorePatterns: ['/docs/search/', '/docs/search/**', '/search/**'],
        },
      } satisfies Preset.Options,
    ],
  ],

  clientModules: [require.resolve('./src/clientModules/a11y-copy-button.js'), require.resolve('./src/clientModules/canonical-fix.js')],
  plugins: [
    require.resolve('./plugins/canonical-overrides.js'),
    'docusaurus-plugin-copy-page-button',
    [
      'docusaurus-plugin-llms',
      {
        generateLLMsTxt: true,
        generateLLMsFullTxt: true,
        title: 'ERDI Docs',
        description: 'Integration guide for ERDI laser rangefinder modules: UART protocols, wiring, code examples and a compatibility matrix.',
      },
    ],
  ],

  themes: [
    [
      '@easyops-cn/docusaurus-search-local',
      {
        hashed: true,
        docsRouteBasePath: '/',
        indexBlog: false,
        indexPages: false,
        language: ['en'],
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
      },
    ],
  ],

  themeConfig: {
    colorMode: {respectPrefersColorScheme: true},
    navbar: {
      title: 'ERDI Docs',
      items: [
        {type: 'docSidebar', sidebarId: 'docs', position: 'left', label: 'Documentation'},
        {to: '/models/', label: 'Models', position: 'left'},
        {to: '/platforms/ardupilot/', label: 'Platforms', position: 'left'},
        {to: '/tools/serial-monitor/', label: 'Serial monitor', position: 'left'},
        {href: 'https://erdilrf.com/models/', label: 'Shop', position: 'right'},
        {href: 'https://github.com/ErdiTech/erdi-docs', label: 'GitHub', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Models', to: '/models/'},
            {label: 'Compatibility', to: '/compatibility/'},
            {label: 'Support', to: '/support/'},
          ],
        },
        {
          title: 'ERDI',
          items: [
            {label: 'erdilrf.com', href: 'https://erdilrf.com/'},
            {label: 'Contact', href: 'https://erdilrf.com/contact/'},
            {label: 'GitHub', href: 'https://github.com/ErdiTech'},
          ],
        },
      ],
      copyright: `ERDI TECH LTD. Code MIT, documentation CC BY 4.0.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'cpp', 'yaml', 'lua', 'ini'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
