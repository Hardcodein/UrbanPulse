import { GetStaticPaths, GetStaticProps, GetStaticPropsContext } from 'next'
import loadNamespaces from 'next-translate/loadNamespaces'
import { ReactElement, ReactNode } from 'react'
import { Main as MainPage } from '@features/pages/main'
import { Main as MainLayout } from '@layouts/main'
import { getI18nPaths } from '@helper/common'

export default function Page(): ReactElement {
  return <MainPage />
}

Page.getLayout = (page: ReactNode) => <MainLayout>{page}</MainLayout>

export const getStaticPaths: GetStaticPaths = () => ({
  fallback: false,
  paths: getI18nPaths(),
})

export const getStaticProps: GetStaticProps = async (ctx: GetStaticPropsContext) => {
  return {
    props: {
      ...(await loadNamespaces({ locale: String(ctx?.params?.locale), pathname: '/' })),
    },
  }
}
