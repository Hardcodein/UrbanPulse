import block from 'bem-css-modules'
import cn from 'classnames'
import { ReactNode, useState } from 'react'
import style from './checkbox.module.sass'

const b = block(style)

type Props = {
  name?: string
  value?: string
  defaultChecked: boolean
  disabled?: boolean
  onClick?: () => void
  onChange?: (checked: boolean) => void
  clickZone?: 'whole' | 'content' | 'control'
  className?: string
  isWholeClick?: boolean
  control?: ReactNode
  children?: ReactNode
}

export function Checkbox(props: Props): JSX.Element {
  const {
    defaultChecked,
    disabled,
    name,
    control,
    children,
    value,
    clickZone = 'control',
    onClick,
    onChange,
    className,
  } = props

  const [checked, setChecked] = useState<boolean>(defaultChecked)

  const handleWholeClick = () => {
    if (disabled || clickZone !== 'whole') return
    onClick && onClick()
    const next = !checked
    setChecked(next)
    onChange && onChange(next)
  }

  const handleContentClick = () => {
    if (disabled || clickZone !== 'content') return
    onClick && onClick()
    const next = !checked
    setChecked(next)
    onChange && onChange(next)
  }

  const handleControlClick = () => {
    if (disabled || clickZone !== 'control') return
  }

  const handleChange = () => {
    if (disabled) return
    const next = !checked
    setChecked(next)
    onChange && onChange(next)
  }

  const classes = cn(className, b({ checked, disabled }))

  return (
    <div className={classes} onClick={handleWholeClick}>
      <input
        name={name}
        type="checkbox"
        checked={checked}
        disabled={disabled}
        onClick={handleControlClick}
        onChange={handleChange}
        className={b('input', { hidden: !!control })}
        value={value}
      />
      {control && (
        <div className={b('control')} onClick={handleControlClick}>
          {control}
        </div>
      )}
      {children && (
        <span className={b('content')} onClick={handleContentClick}>
          {children}
        </span>
      )}
    </div>
  )
}
