import { GetStaticPaths, GetStaticProps, GetStaticPropsContext } from 'next'
import loadNamespaces from 'next-translate/loadNamespaces'
import { ReactElement, ReactNode } from 'react'
import { Calculations as CalculationsPage } from '@features/pages/calculations'
import { Second as SecondLayout } from '@layouts//second'
import { getI18nPaths } from '@helper/common'

export default function Page(): ReactElement {
  return <CalculationsPage />
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
