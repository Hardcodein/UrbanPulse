import block from 'bem-css-modules'
import Image from 'next/image'
import style from './logo.module.sass'

const b = block(style)

export function Logo(): JSX.Element {
  return (
    <div className={b()}>
      <Image
        alt="HomeHub"
        src={require(`./images/logo.svg`)}
        width={50}
        height={50}
        priority={true}
      />
    </div>
  )
}
