import block from 'bem-css-modules'
import { Button } from '@ui/button'
import { IconHub, IconHubNames, IconHubTypes } from '@ui/icon-hub'
import style from './control.module.sass'

const b = block(style)

type Props = {
  iconType: IconHubTypes
  iconName: IconHubNames
  iconFill?: string
  size?: string
  is?: string
  loading?: boolean
  onClick?: () => void
}

export function Control({
  iconType,
  iconName,
  iconFill,
  is,
  size,
  loading,
  onClick,
}: Props): JSX.Element {
  return (
    <Button onClick={onClick} className={b({ size, is })}>
      <IconHub
        type={iconType}
        rotation={loading}
        name={iconName}
        fill={iconFill}
        width={22}
        height={22}
      />
    </Button>
  )
}
