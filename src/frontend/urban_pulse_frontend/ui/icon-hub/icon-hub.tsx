import { IconImg, IconImgList } from '@ui/icon-img'
import { IconSvg, IconSvgList } from '@ui/icon-svg'
import { iconHubColor, IconHubTypes, IconHubNames } from './icon-hub.const'

type Props = {
  className?: string
  fill?: string
  width?: number
  height?: number
  rotation?: boolean
  type: IconHubTypes
  name: IconHubNames
}

export function IconHub(props: Props): JSX.Element {
  const { type, name, fill = iconHubColor.DARK_GRAY, width = 16, height = 16, ...rest } = props
  switch (type) {
    case IconHubTypes.IMG:
      return <IconImg width={width} name={name as IconImgList} height={height} {...rest} />

    case IconHubTypes.SVG:
      return (
        <IconSvg fill={fill} name={name as IconSvgList} width={width} height={height} {...rest} />
      )

    default:
      return <>Type is required</>
  }
}
