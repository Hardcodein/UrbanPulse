import block from 'bem-css-modules'
import { CSSTransition } from 'react-transition-group'
import style from './transition.module.sass'

const b = block(style)

type Props = {
  show: boolean
  entity: string
  timeout?: number
  unmountOnExit: boolean
  children: (JSX.Element | string)[] | JSX.Element | string
}

export function Transition({ show, entity, timeout = 600, children, ...args }: Props): JSX.Element {
  return (
    <CSSTransition
      in={show}
      classNames={{
        enter: b({ [entity]: 'enter' }),
        enterActive: b({ [entity]: 'enter-active' }),
        exit: b({ [entity]: 'exit' }),
        exitActive: b({ [entity]: 'exit-active' }),
      }}
      timeout={timeout}
      {...args}
    >
      <div className="tn">{children}</div>
    </CSSTransition>
  )
}
