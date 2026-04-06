import block from 'bem-css-modules'
import cn from 'classnames'
import { LangSwitcher } from '@features/common/lang-switcher'
import { MenuMain } from '@features/common/menu'
import style from './header.module.sass'

const b = block(style)

type Props = {
  className?: string
}

export function Header({ className }: Props): JSX.Element {
  const classes = cn(b(), className)
  return (
    <div className={classes}>
      <MenuMain />
      <LangSwitcher />
    </div>
  )
}
