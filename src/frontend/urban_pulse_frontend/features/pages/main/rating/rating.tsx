import block from 'bem-css-modules'
import cn from 'classnames'
import { Radio } from '@ui/radio'
import style from './rating.module.sass'

const b = block(style)

type Props = {
  name: string
  desc?: string
  className?: string
  ranges: Array<string | number>
}

export function Rating({ className, name, desc, ranges }: Props): JSX.Element {
  const classes = cn(b(), className)
  return (
    <div className={classes}>
      {desc && <div className={b('desc')}>{desc}</div>}
      <div className={b('content')}>
        {ranges.map((range) => (
          <Radio key={range} value={range} name={name}>
            {range}
          </Radio>
        ))}
      </div>
    </div>
  )
}
