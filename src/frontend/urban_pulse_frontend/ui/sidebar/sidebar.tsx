import block from 'bem-css-modules'
import cn from 'classnames'
import { ReactNode } from 'react'
import style from './sidebar.module.sass'

const b = block(style)

type Props = {
  header?: ReactNode
  footer?: ReactNode
  className?: string
  onMouseOver?: () => void
  onMouseLeave?: () => void
  children: ReactNode
}

export function Sidebar({
  header,
  footer,
  children,
  className,
  onMouseOver,
  onMouseLeave,
}: Props): JSX.Element {
  const handleMouseOver = () => {
    onMouseOver && onMouseOver()
  }
  const handleMouseLeave = () => {
    onMouseLeave && onMouseLeave()
  }

  const classes = cn(b(), className)
  return (
    <div className={classes} onMouseOver={handleMouseOver} onMouseLeave={handleMouseLeave}>
      {header && <div className={b('header')}>{header}</div>}
      <div className={b('content')}>{children}</div>
      {footer && <div className={b('footer')}>{footer}</div>}
    </div>
  )
}
