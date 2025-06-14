import { GetStaticPaths, GetStaticProps, GetStaticPropsContext } from 'next'
import loadNamespaces from 'next-translate/loadNamespaces'
import { ReactElement, ReactNode } from 'react'
import { About as AboutPage } from '@features/pages/about'
import { Second as SecondLayout } from '@layouts/second'
import { getI18nPaths } from '@helper/common'

export default function Page(): ReactElement {
  return <AboutPage />
}

Page.getLayout = (page: ReactNode) => <SecondLayout>{page}</SecondLayout>

export const getStaticPaths: GetStaticPaths = () => ({
  fallback: false,
  paths: getI18nPaths(),
})

export const getStaticProps: GetStaticProps = async (ctx: GetStaticPropsContext) => {
  return {
    props: {
      ...(await loadNamespaces({ locale: String(ctx?.params?.locale), pathname: '/about' })),
    },
  }
}
