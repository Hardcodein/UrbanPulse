import block from 'bem-css-modules'
import { Link } from '@ui/link'
import style from './lang-switcher.module.sass'

const b = block(style)

export function LangSwitcher(): JSX.Element {
  return (
    <div className={b()}>
      <Link className={b('link')} locale="ru">
        ru
      </Link>
      <Link className={b('link')} locale="en">
        en
      </Link>
    </div>
  )
}
