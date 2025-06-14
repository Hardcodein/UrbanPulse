import isObject from 'lodash/isObject'
import isString from 'lodash/isString'
import NLink from 'next/link'
import { useRouter } from 'next/router'
import React, { PropsWithChildren, ReactElement } from 'react'
import { UrlObject } from 'url'
import { LinkLocaleNone } from '@ui/link'

type Url = string | UrlObject

type Props = {
  href?: Url
  as?: Url
  className?: string
  replace?: boolean
  scroll?: boolean
  shallow?: boolean
  passHref?: boolean
  prefetch?: boolean
  locale?: string | false
}

export function Link({
  className,
  locale,
  href,
  children,
  ...rest
}: PropsWithChildren<Props>): ReactElement {
  const router = useRouter()
  locale = locale || router.locale

  if (!locale || locale === LinkLocaleNone) {
    return (
      <NLink href={href || router.asPath} locale={undefined} {...rest}>
        <a className={className}>{children}</a>
      </NLink>
    )
  }

  if (locale) {
    const query = { ...router.query }
    delete query.locale
    let linkHref: Url = {
      query,
      pathname: router.pathname.replace('[locale]', locale),
    }

    if (isString(href)) {
      linkHref = `/${locale}${href}`
    }

    if (isObject(href)) {
      linkHref = { ...href, pathname: `/${locale}${href.pathname}` }
    }

    return (
      <NLink href={linkHref} locale={undefined} {...rest}>
        <a className={className}>{children}</a>
      </NLink>
    )
  }

  return <></>
}
