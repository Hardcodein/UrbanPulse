import { ReactNode } from 'react'

type Props = {
  className?: string
  children?: ReactNode
}

export function MapChunk({ children, className }: Props): JSX.Element {
  return <div className={className}>{children}</div>
}
