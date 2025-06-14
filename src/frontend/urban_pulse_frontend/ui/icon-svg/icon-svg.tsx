import block from 'bem-css-modules'
import cn from 'classnames'
import { FC, SVGProps, useState, useEffect } from 'react'
import { IconSvgList } from '@ui/icon-svg'
import style from './icon-svg.module.sass'

const b = block(style)

export type Props = {
  className?: string
  fill?: string
  width: number
  height: number
  rotation?: boolean
} & {
  name: IconSvgList
}

export function IconSvg({ className, name, rotation, ...rest }: Props): JSX.Element | null {
  const [Icon, setIcon] = useState<FC<SVGProps<SVGSVGElement>> | string>('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    const importIcon = async (): Promise<void> => {
      try {
        setIcon(
          (await import(`!!@svgr/webpack?-svgo,+titleProp,+ref!./images/${name}.svg`)).default
        )
        // eslint-disable-next-line no-useless-catch
      } catch (err) {
        throw err
      } finally {
        setLoading(false)
      }
    }
    importIcon()
  }, [name])

  let inner: JSX.Element = <></>

  if (loading) inner = <></>
  if (!loading && Icon) inner = <Icon {...rest} />

  const classes = cn(className, `icon-svg_name_${name.replace('/', '-')}`, b({ rotation }))
  return (
    <div className={classes} style={{ width: rest.width, height: rest.height }}>
      {inner}
    </div>
  )
}
