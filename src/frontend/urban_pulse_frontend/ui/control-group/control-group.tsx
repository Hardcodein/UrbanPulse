import block from 'bem-css-modules'
import style from './control-group.module.sass'

const b = block(style)

type Props = {
  direction?: string
  children: JSX.Element | string | (JSX.Element | string)[]
}

export function ControlGroup({ children, direction }: Props): JSX.Element {
  return <div className={b({ direction })}>{children}</div>
}
