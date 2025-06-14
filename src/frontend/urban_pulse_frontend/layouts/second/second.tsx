import block from 'bem-css-modules'
import { ReactNode } from 'react'
import { Header } from '@features/common/header'
import { DefaultHead } from '@layouts/default-head'
import style from './second.module.sass'

const b = block(style)

type Props = {
  children: ReactNode
}

export function Second({ children }: Props): JSX.Element {
  return (
    <div className={b()}>
      <DefaultHead />
      <Header />
      {children}
    </div>
  )
}
