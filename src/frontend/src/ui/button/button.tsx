import block from 'bem-css-modules'
import cn from 'classnames'
import { ReactNode } from 'react'
import { Buttons } from '@ui/button'
import style from './button.module.sass'

const b = block(style)

type Props = {
  onClick?: () => void
  className?: string
  theme?: Buttons
  children?: ReactNode
}

export function Button({ onClick, theme, className, children }: Props): JSX.Element {
  const classes = cn(className, b({ theme }))
  return (
    <button onClick={onClick} className={classes}>
      {children}
    </button>
  )
}
