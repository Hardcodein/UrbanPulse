import block from 'bem-css-modules'
import { useContext } from 'react'
import { Checkbox } from '@ui/checkbox'
import { Rating } from '@features/pages/main/rating'
import { MapContext } from '@ui/map/map.context'
import style from './form_filter.module.sass'

const b = block(style)

const useMap = () => useContext(MapContext)

type Layer = {
  id: string
  label: string
  type: 'rating' | 'availability'
  desc?: string
  name?: string
  ranges?: Array<string | number>
}

const LAYERS: Layer[] = [
  {
    id: 'analytics_hex_infrastructure',
    label: 'Доступность социальной инфраструктуры',
    type: 'rating',
    desc: 'Доступность социальной инфраструктуры',
    name: 'infrastructure',
    ranges: [1, 2, 3, 4, 5],
  },
  {
    id: 'analytics_hex',
    label: 'Плотность застройки',
    type: 'rating',
    desc: 'Плотность застройки',
    name: 'buildings',
    ranges: [1, 2, 3, 4, 5],
  },
  {
    id: 'analytics_hex_air',
    label: 'Экологическая обстановка',
    type: 'rating',
    desc: 'Экологическая обстановка',
    name: 'air',
    ranges: [1, 2, 3, 4, 5],
  },
  {
    id: 'analytics_hex_life_quality',
    label: 'Качество жизни',
    type: 'rating',
    desc: 'Качество жизни',
    name: 'life_quality',
    ranges: [1, 2, 3, 4, 5],
  },
]

export function FormFilter(): JSX.Element {
  const map = useMap()

  const handleCheckboxChange = (layerId: string, isChecked: boolean) => {
    if (!map?.isStyleLoaded()) return
    map.setLayoutProperty(layerId, 'visibility', isChecked ? 'visible' : 'none')
  }

  const handleReset = () => {
    LAYERS.forEach(({ id }) => {
      if (map?.isStyleLoaded()) {
        map.setLayoutProperty(id, 'visibility', 'none')
      }
    })
  }

  return (
    <div className={b({ filter: true })}>
      {LAYERS.map((layer) => (
        <div key={layer.id}>
          <Checkbox
            defaultChecked={false}
            onChange={(isChecked) => handleCheckboxChange(layer.id, isChecked)}
          >
            <Rating
              desc={layer.desc}
              name={layer.name ?? layer.id}
              ranges={layer.ranges ?? [1, 2, 3, 4, 5]}
            />
          </Checkbox>
        </div>
      ))}
      <div>
        <button onClick={handleReset}>Сбросить</button>
      </div>
    </div>
  )
}
