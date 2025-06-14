import block from 'bem-css-modules'
import useTranslation from 'next-translate/useTranslation'
import { Link } from '@ui/link'
import { menu } from './menu_main.const'
import style from './menu_main.module.sass'

const b = block(style)

export function MenuMain(): JSX.Element {
  const { t } = useTranslation('common')
  return (
    <div className={b({ main: true })}>
      {menu.map((item) => (
        <Link className={b('item')} href={item.href} key={item.name}>
          {t(item.name)}
        </Link>
      ))}
    </div>
  )
}
