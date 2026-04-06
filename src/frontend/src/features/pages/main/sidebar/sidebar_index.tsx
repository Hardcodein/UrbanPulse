import block from 'bem-css-modules'
import { Card } from '@features/pages/main/card'
import { FormFilter } from '@features/pages/main/form'
import { Sidebar } from '@ui/sidebar'
import style from './sidebar_index.module.sass'

const b = block(style)

export function SidebarIndex(): JSX.Element {
  return (
    <Sidebar className={b({ index: true })}>
      <Card title={'Фильтры'}>
        <FormFilter />
      </Card>
    </Sidebar>
  )
}
