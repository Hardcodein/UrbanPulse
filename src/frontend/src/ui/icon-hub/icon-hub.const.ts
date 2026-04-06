import { IconImgList } from '@ui/icon-img'
import { IconSvgList } from '@ui/icon-svg'

export enum IconHubTypes {
  IMG = 'img',
  SVG = 'svg',
}

export type IconHubNames = IconSvgList | IconImgList

export const iconHubList = { ...IconSvgList, ...IconImgList }
export const iconHubColor = {
  DARK_GRAY: '#2C2D2E',
}
