import { Select } from '@ui/select'

type Props = {
  destination?: string
}

export function AvailabilityRow({ destination }: Props): JSX.Element {
  const dest = destination ? (
    destination
  ) : (
    <Select>
      <option value="kindergarten">дет. сад</option>
      <option value="to-eat">поесть</option>
    </Select>
  )
  return (
    <>
      До {dest}{' '}
      <Select>
        <option value="5">5 минут</option>
        <option value="10">10 минут</option>
        <option value="15">15 минут</option>
        <option value="30">30 минут</option>
        <option value="60">60 минут</option>
      </Select>{' '}
      на{' '}
      <Select>
        <option value="auto">Авто</option>
        <option value="foot">Ногах</option>
        <option value="sledge">Санках</option>
      </Select>
    </>
  )
}
