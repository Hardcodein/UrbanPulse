import block from 'bem-css-modules'
import cn from 'classnames'
import maplibregl from 'maplibre-gl'
import { ReactNode, useEffect, useRef, useState } from 'react'
import { IconHub, iconHubColor, iconHubList, IconHubTypes } from '@ui/icon-hub'
import { MapProvider } from '@ui/map/map.context'
import { Transition } from '@ui/transition'
import style from './map.module.sass'

const b = block(style)

export type Viewport = {
  lng: number
  lat: number
  zoom: number
}

export type PropsEvents = {
  onMoveStart?: () => void
  onMoveEnd?: (viewport: Viewport) => void
  onStyleDataLoading?: () => void
  onStyleData?: () => void
  onLoad?: () => void
  onClick?: (e: maplibregl.MapMouseEvent) => void
  onRightClick?: (e: maplibregl.MapMouseEvent) => void
}

type Props = {
  lng: number
  lat: number
  zoom: number
  style?: maplibregl.Style
  className?: string
  children?: ReactNode
  preserveDrawingBuffer?: boolean
} & PropsEvents

export function Map({
  lng,
  lat,
  zoom,
  style,
  className,
  children,
  preserveDrawingBuffer = false,
  onMoveStart,
  onMoveEnd,
  onStyleDataLoading,
  onStyleData,
  onLoad,
  onClick,
  onRightClick,
}: Props): JSX.Element {
  const map = useRef<maplibregl.Map | null>(null)
  const mapContainer = useRef<HTMLDivElement>(null)
  const [isStyleLoading, setStyleLoading] = useState(true)
  const [calledFromMoveEnd, setCalledFromMoveEnd] = useState(false)

  /* initialize map */
  useEffect(() => {
    if (!mapContainer.current) return

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      zoom: zoom,
      center: [lng, lat],
      style: style as maplibregl.Style,
      hash: false,
      attributionControl: true,
      renderWorldCopies: false,
      maxBounds: [
        [-180, -85],
        [180, 85],
      ],
      preserveDrawingBuffer,
    })

    window.__MAP = map.current

    const ro = new ResizeObserver(() => map.current?.resize())
    ro.observe(mapContainer.current)

    return () => {
      window.__MAP = null

      map.current?.remove()
      if (mapContainer.current) ro.unobserve(mapContainer.current as Element)
    }
  }, [])

  /* init listeners */
  useEffect(() => {
    map.current?.on('movestart', mapOnMoveStartListener)
    map.current?.on('moveend', mapOnMoveEndListener)
    map.current?.on('styledataloading', mapOnStyleDataLoading)
    map.current?.on('styledata', mapOnStyleData)
    map.current?.on('load', mapOnLoad)
    map.current?.on('click', mapOnClickListener)
    map.current?.on('contextmenu', mapOnContextMenuListener)

    return () => {
      map.current?.off('movestart', mapOnMoveStartListener)
      map.current?.off('moveend', mapOnMoveEndListener)
      map.current?.off('styledataloading', mapOnStyleDataLoading)
      map.current?.off('styledata', mapOnStyleData)
      map.current?.off('load', mapOnLoad)
      map.current?.off('click', mapOnClickListener)
      map.current?.off('contextmenu', mapOnContextMenuListener)
    }
  })

  /* update style */
  useEffect(() => {
    if (!style) return
    setStyleLoading(true)
    map.current?.setStyle(style)
  }, [style])

  /* update coords */
  useEffect(() => {
    if (calledFromMoveEnd) return
    map.current?.flyTo({ center: [lng, lat], zoom })

    // console.log('UPDATE lng lat zoom', lng, lat, zoom)
  }, [lng, lat, zoom])

  const mapOnMoveStartListener = () => {
    onMoveStart && onMoveStart()
  }

  const mapOnMoveEndListener = () => {
    const coords = map.current?.getCenter()
    const lng = Number(coords?.lng.toFixed(6))
    const lat = Number(coords?.lat.toFixed(6))
    const zoom = Number(map.current?.getZoom().toFixed(2))

    setCalledFromMoveEnd(true)
    onMoveEnd && onMoveEnd({ lng, lat, zoom })
    setCalledFromMoveEnd(false)
  }

  const mapOnStyleDataLoading = () => {
    waiting()
    onStyleDataLoading && onStyleDataLoading()
  }

  const mapOnStyleData = () => {
    waiting()
    onStyleData && onStyleData()
  }

  const mapOnLoad = () => {
    waiting()
    onLoad && onLoad()
  }

  const mapOnClickListener = (e: maplibregl.MapMouseEvent) => {
    if (e.lngLat.lng >= 180 || e.lngLat.lng <= -180) return
    onClick && onClick(e)
  }

  const mapOnContextMenuListener = (e: maplibregl.MapMouseEvent) => {
    if (e.lngLat.lng >= 180 || e.lngLat.lng <= -180) return
    onRightClick && onRightClick(e)
  }

  const waiting = () => {
    if (!map.current?.isStyleLoaded()) {
      setTimeout(waiting, 200)
    } else {
      setStyleLoading(false)
    }
  }

  const classes = cn('mmrgl-map', b(), className)

  return (
    <MapProvider map={map.current}>
      <div ref={mapContainer} className={classes}>
        <Transition show={isStyleLoading} entity={'map-spinner'} timeout={300} unmountOnExit>
          <div className={b('spinner')}>
            <IconHub
              fill={iconHubColor.DARK_GRAY}
              type={IconHubTypes.SVG}
              width={32}
              height={32}
              rotation={true}
              name={iconHubList.ACTION_SPINNER}
            />
          </div>
        </Transition>

        {children}
      </div>
    </MapProvider>
  )
}
