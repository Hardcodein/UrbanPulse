import block from 'bem-css-modules'
import { ReactNode } from 'react'
import style from './radio.module.sass'

const b = block(style)

type Props = {
  name: string
  value: string | number
  children?: ReactNode
}

export function Radio({ name, value, children }: Props): JSX.Element {
  return (
    <label className={b()} tabIndex={0} role={'button'}>
      <input className={b('input')} type="radio" name={name} value={value} />
      {children && <span className={b('content')}>{children}</span>}
    </label>
  )
}
