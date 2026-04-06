const withPlugins = require('next-compose-plugins')
const eslintConfig = require('./.eslintrc.js')
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
})
const ForkTsCheckerWebpackPlugin = require('fork-ts-checker-webpack-plugin')
const ForkTsCheckerNotifierWebpackPlugin = require('fork-ts-checker-notifier-webpack-plugin')

const regexEqual = (x, y) =>
  x instanceof RegExp &&
  y instanceof RegExp &&
  x.source === y.source &&
  x.global === y.global &&
  x.ignoreCase === y.ignoreCase &&
  x.multiline === y.multiline

module.exports = withPlugins([withBundleAnalyzer], {
  trailingSlash: true,
  images: {
    loader: 'imgix',
    path: '/',
  },
  webpack: (config, options) => {
    const sassModuleRules = config.module.rules[2].oneOf.find((rule) =>
      regexEqual(rule.test, /\.module\.(scss|sass)$/)
    )
    const cssLoader = sassModuleRules.use.find((use) => use.loader.includes('css-loader'))
    cssLoader.options.modules.getLocalIdent = (context, localIdentName, localName) => localName

    const { dev, isServer } = options

    if (dev && isServer && process.env.TS_CHECK === 'true') {
      config.plugins.push(
        new ForkTsCheckerWebpackPlugin({
          eslint: {
            ...eslintConfig,
            files: '**/*.{ts,tsx,js,jsx}',
          },
        })
      )

      if (process.env.TS_CHECK_NOTIFY === 'true') {
        config.plugins.push(
          new ForkTsCheckerNotifierWebpackPlugin({
            skipSuccessful: process.env.TS_CHECK_NOTIFY_SUCCESS !== 'true',
          })
        )
      }
    }

    return config
  },
})
