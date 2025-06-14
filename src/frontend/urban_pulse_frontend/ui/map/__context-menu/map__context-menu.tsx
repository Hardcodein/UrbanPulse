import block from 'bem-css-modules'
import { RefObject } from 'react'
import style from './map__context-menu.module.sass'

const b = block(style)

type Props = {
  show: boolean
  top: number
  left: number
  offsetTop?: number
  offsetLeft?: number
  caption: string
  pin: string
  menuRef: RefObject<HTMLDivElement>
  onItemClick?: () => void
}

export function MapContextMenu({
  show = false,
  left = 0,
  top = 0,
  offsetTop = -15,
  offsetLeft = 5,
  caption,
  menuRef,
}: Props): JSX.Element {
  return (
    <div
      className={b('context-menu')}
      ref={menuRef}
      style={{ top: top + offsetTop, left: left + offsetLeft }}
    >
      {show && caption}
    </div>
  )
}
