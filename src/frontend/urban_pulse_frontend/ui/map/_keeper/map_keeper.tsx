import _isEqual from 'lodash/isEqual'
import mapboxgl from 'mapbox-gl'
import { useRouter } from 'next/router'
import { ReactNode, useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Map, PropsEvents, Viewport } from '@ui/map'
import { actions as mapActions } from '@redux/map'
import { RootState } from '@redux/reducers'

type Props = {
  className?: string
  preserveDrawingBuffer?: boolean
  disableUrlUpdate?: boolean
  style?: mapboxgl.Style
  children?: ReactNode
} & PropsEvents

export function MapKeeper({
  className,
  style,
  preserveDrawingBuffer,
  disableUrlUpdate,
  onMoveStart,
  onMoveEnd,
  onClick,
  onRightClick,
  children,
}: Props): JSX.Element {
  const [isMount, setIsMount] = useState<boolean>(false)
  const [prevViewport, setPrevViewport] = useState<Viewport | null>(null)

  const dispatch = useDispatch()
  const router = useRouter()

  const lng: number = useSelector((state: RootState) => state.map.lng)
  const lat: number = useSelector((state: RootState) => state.map.lat)
  const zoom: number = useSelector((state: RootState) => state.map.zoom)

  const mapSetDragging = (dragging: boolean) => dispatch(mapActions.setDragging(dragging))
  const mapSetViewport = (viewport: Viewport) => {
    if (disableUrlUpdate || _isEqual(viewport, prevViewport)) return

    setPrevViewport(viewport)

    dispatch(mapActions.setViewport(viewport))

    router.replace({
      query: { ...router.query, ...viewport },
    })
  }

  useEffect(() => {
    const urlSearchParams = new URLSearchParams(window.location.search)
    const params = Object.fromEntries(urlSearchParams.entries())
    const lng = Number(params.lng)
    const lat = Number(params.lat)
    const zoom = Number(params.zoom)

    if (lng && lat && zoom) {
      mapSetViewport({ lng, lat, zoom })
    }
    setIsMount(true)
  }, [])

  const handleMoveStart = () => {
    mapSetDragging(true)
    onMoveStart && onMoveStart()
  }

  const handleMoveEnd = (viewport: Viewport) => {
    mapSetViewport(viewport)
    mapSetDragging(false)
    onMoveEnd && onMoveEnd(viewport)
  }

  const handleClick = (e: mapboxgl.MapMouseEvent) => {
    onClick && onClick(e)
  }

  const handleRightClick = (e: mapboxgl.MapMouseEvent) => {
    onRightClick && onRightClick(e)
  }

  const handleOnLoad = () => {
    mapSetViewport({ lng, lat, zoom })
  }

  if (!isMount) return <></>
  return (
    <Map
      className={className}
      lng={lng}
      lat={lat}
      zoom={zoom}
      style={style}
      accessToken='pk.eyJ1Ijoicnlhbm1pbnRlcjA4IiwiYSI6ImNtOXN5endrbTA2MDMyaXBvdm1hNW96bmMifQ.qumSdswJwxqVGwqULikudw'
      preserveDrawingBuffer={preserveDrawingBuffer}
      onClick={handleClick}
      onLoad={handleOnLoad}
      onRightClick={handleRightClick}
      onMoveStart={handleMoveStart}
      onMoveEnd={handleMoveEnd}
    >
      {children}
    </Map>
  )
}
