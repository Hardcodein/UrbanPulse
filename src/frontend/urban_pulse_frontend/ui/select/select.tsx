import block from 'bem-css-modules'
import cn from 'classnames'
import { ChangeEvent, ReactNode, useRef } from 'react'
import style from './select.module.sass'

const b = block(style)

type Props = {
  name?: string
  className?: string
  children: ReactNode
  onChange?: (e: ChangeEvent<HTMLSelectElement>) => void
}

export function Select({ name, className, onChange, children }: Props): JSX.Element {
  const handleChange = (e: ChangeEvent<HTMLSelectElement>) => {
    onChange && onChange(e)
  }

  const classes = cn(b(), className)

  return (
    <select name={name} className={classes} onChange={handleChange}>
      {children}
    </select>
  )
}
