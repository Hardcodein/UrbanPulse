import { useClickAway } from 'ahooks'
import block from 'bem-css-modules'
import cn from 'classnames'
import mapboxgl from 'mapbox-gl'
import { useEffect, useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import {
  MapControlsBottomRight,
  MapControlsCenterRight,
  MapControlsTopRight,
} from '@features/pages/main/map-controls'
import { MapContextMenu, MapControlPositions, MapControls, MapKeeper } from '@ui/map'
import { MapControlDirections } from '@ui/map/__controls/map__controls.const'
import { RootState } from '@redux/reducers'
import style from './map_main.module.sass'
import mapStyle from './map_main.style.json'

const b = block(style)

type contextMenuProps = {
  lng: number
  lat: number
  x: number
  y: number
}

type Props = {
  className?: string
}

export function MapMain({ className }: Props): JSX.Element {
  const menuRef = useRef<HTMLDivElement>(null)
  const defaultContextMenuData = { lng: 0, lat: 0, x: 0, y: 0 }
  const [contextMenuData, setContextMenuData] = useState<contextMenuProps>(defaultContextMenuData)
  const [showContextMenu, setShowContextMenu] = useState<boolean>(false)

  const dragging: boolean = useSelector((state: RootState) => state.map.dragging)

  useClickAway(() => {
    setShowContextMenu(false)
  }, menuRef)

  useEffect(() => {
    setShowContextMenu(false)
  }, [dragging])

  const handleClick = (e: mapboxgl.MapMouseEvent) => {
    console.log(e.lngLat)
  }

  const handleRightClick = (e: mapboxgl.MapMouseEvent) => {
    const lng = Number(e.lngLat.lng.toFixed(6))
    const lat = Number(e.lngLat.lat.toFixed(6))

    setContextMenuData({ lng, lat, ...e.point })
    setShowContextMenu(true)
  }

  const handleContextItemClick = () => {
    setShowContextMenu(false)
  }

  const classes = cn(b({ main: true }), className)

  return (
    <MapKeeper
      style={mapStyle as mapboxgl.Style}
      className={classes}
      onClick={handleClick}
      onRightClick={handleRightClick}
    >
      <MapContextMenu
        caption={`${contextMenuData.lat}, ${contextMenuData.lng}`}
        pin={`${contextMenuData.lng},${contextMenuData.lat}`}
        menuRef={menuRef}
        show={showContextMenu}
        top={contextMenuData.y}
        left={contextMenuData.x}
        onItemClick={handleContextItemClick}
      />
      <MapControls position={MapControlPositions.TOP_RIGHT}>
        <MapControlsTopRight />
      </MapControls>
      <MapControls
        position={MapControlPositions.CENTER_RIGHT}
        direction={MapControlDirections.VERTICAL}
      >
        <MapControlsCenterRight />
      </MapControls>
      <MapControls position={MapControlPositions.BOTTOM_RIGHT}>
        <MapControlsBottomRight />
      </MapControls>
    </MapKeeper>
  )
}
