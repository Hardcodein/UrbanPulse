import block from 'bem-css-modules'
import { ReactNode } from 'react'
import { MapControlDirections, MapControlPositions } from '@ui/map/__controls/map__controls.const'
import style from './map__controls.module.sass'

const b = block(style)

type Props = {
  position: MapControlPositions
  direction?: MapControlDirections
  children: ReactNode
}

export function MapControls({
  position,
  direction = MapControlDirections.HORIZONTAL,
  children,
}: Props): JSX.Element {
  return <div className={b('controls', { [position]: !!position, direction })}>{children}</div>
}
