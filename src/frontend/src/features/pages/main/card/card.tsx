import block from 'bem-css-modules'
import cn from 'classnames'
import { ReactNode } from 'react'
import style from './card.module.sass'

const b = block(style)

type Props = {
  className?: string
  title?: string
  type?: string
  shadow?: boolean
  headerContent?: ReactNode
  children: ReactNode
  onCloseClick?: () => void
}

export function Card({
  className,
  title,
  shadow = true,
  onCloseClick,
  headerContent,
  children,
}: Props): JSX.Element {
  const showHeader = title || headerContent || onCloseClick
  const classes = cn(className, b({ shadow }))

  return (
    <div className={classes}>
      {showHeader && (
        <div className={b('header')}>
          {title && <div className={b('title')}>{title}</div>}
          {headerContent}
        </div>
      )}
      <div className={b('content')}>{children}</div>
    </div>
  )
}
