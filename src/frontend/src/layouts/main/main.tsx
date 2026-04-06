import block from 'bem-css-modules'
import { ReactNode } from 'react'
import { Header } from '@features/common/header'
import { MapMain } from '@features/pages/main/map'
import { DefaultHead } from '@layouts/default-head'
import style from './main.module.sass'

const b = block(style)

type Props = {
  children: ReactNode
}

export function Main({ children }: Props): JSX.Element {
  return (
    <div className={b()}>
      <DefaultHead />
      <Header className={b('header')} />
      <div className={b('elements')}>
        {children}
        <MapMain />
      </div>
    </div>
  )
}
