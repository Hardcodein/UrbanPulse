import block from 'bem-css-modules'
import cn from 'classnames'
import { ChangeEvent } from 'react'
import style from './input.module.sass'

const b = block(style)

type Props = {
  value?: string
  placeholder?: string
  transparent?: boolean
  className?: string
  mix?: string
  onFocus?: () => void
  onBlur?: () => void
  onChange?: (e: ChangeEvent<HTMLInputElement>) => void
}

export function Input({
  value,
  placeholder,
  transparent = false,
  className,
  mix,
  onFocus,
  onBlur,
  onChange,
}: Props): JSX.Element {
  const classes = cn(className, b({ transparent, mix }))
  return (
    <input
      onFocus={onFocus}
      onBlur={onBlur}
      value={value}
      onChange={onChange}
      className={classes}
      placeholder={placeholder}
    />
  )
}
