import block from 'bem-css-modules'
import { Sidebar } from '@ui/sidebar'
import style from './sidebar_index.module.sass'

const b = block(style)

export function SidebarIndex(): JSX.Element {
  return (
    <Sidebar className={b({ index: true })} header={<>header</>} footer={<>footer</>}>
      index
    </Sidebar>
  )
}
