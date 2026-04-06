import 'mapbox-gl/dist/mapbox-gl.css'
import appWithI18n from 'next-translate/appWithI18n'
import type { AppProps } from 'next/app'
import { useRouter } from 'next/router'
import { ReactNode, useEffect } from 'react'
import { Provider } from 'react-redux'
import { PersistGate } from 'redux-persist/integration/react'
import { useStore } from '@redux/store'
import i18nConfig from '../i18n'
import '../styles/globals.sass'

type Props = {
  Component: {
    getLayout: (component: JSX.Element) => JSX.Element
  }
} & AppProps

function MyApp({ Component, pageProps }: Props): JSX.Element {
  const { store, persistor } = useStore(pageProps.initialReduxState)

  const getLayout = Component.getLayout || ((page: ReactNode) => page)

  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        {getLayout(<Component {...pageProps} />)}
      </PersistGate>
    </Provider>
  )
}

// @ts-ignore
const TranslatedApp = appWithI18n(MyApp, {
  ...i18nConfig,
  skipInitialProps: true,
})

// because we do not use the i18n feature of next.js
export default function RouterEmulatedApp({ ...props }: Props): JSX.Element {
  const router = useRouter()
  router.locale = String(router.query.locale)
  router.locales = i18nConfig.locales

  useEffect(() => {
    router.defaultLocale =
      i18nConfig.locales.find((locale) => navigator?.language?.startsWith(locale)) ||
      i18nConfig.defaultLocale
  })

  return <TranslatedApp {...props} />
}
