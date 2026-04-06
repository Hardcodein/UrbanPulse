import { GetStaticProps } from 'next'
import { useRouter } from 'next/router'
import { ReactElement, useEffect } from 'react'
import i18nConfig from '../i18n'

export const getStaticProps: GetStaticProps = () => ({
  props: {
    locales: i18nConfig.locales,
  },
})

type Props = {
  locales: Array<string>
}

export default function Main({ locales }: Props): ReactElement {
  const router = useRouter()

  // language detection
  useEffect(() => {
    if (!navigator?.language) {
      router.replace('/' + router.defaultLocale)
    }

    if (navigator?.language) {
      const browserLocale =
        locales.find((locale) => navigator.language?.startsWith(locale)) || router.defaultLocale

      router.replace('/' + browserLocale)
    }
  }, [])

  return <></>
}
