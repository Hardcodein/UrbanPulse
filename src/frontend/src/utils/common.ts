import i18nConfig from '../i18n'

export const getI18nPaths = (): { params: { locale: string } }[] =>
  i18nConfig.locales.map((lng) => ({
    params: {
      locale: lng,
    },
  }))
