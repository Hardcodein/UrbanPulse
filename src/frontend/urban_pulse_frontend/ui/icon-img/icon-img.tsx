import block from 'bem-css-modules'
import { IconImgList } from '@ui/icon-img'
import style from './icon-img.module.sass'

const b = block(style)

export type Props = {
  name: IconImgList
  width: number
  height: number
}

export function IconImg({ name, width = 16, height = 16 }: Props): JSX.Element {
  return <i className={b({ [name]: !!name, size: `${width}x${height}` })} />
}
