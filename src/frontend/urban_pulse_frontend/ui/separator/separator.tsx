import block from 'bem-css-modules'
import style from './separator.module.sass'

const b = block(style)

type Prop = {
  position: string
  theme: string
}

export function Separator({ position, theme }: Prop): JSX.Element {
  return <div className={b({ position, theme })} />
}
