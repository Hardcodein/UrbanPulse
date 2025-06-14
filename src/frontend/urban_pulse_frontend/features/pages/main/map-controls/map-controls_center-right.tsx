import { useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Control } from '@ui/control'
import { ControlGroup } from '@ui/control-group'
import { iconHubList, IconHubTypes } from '@ui/icon-hub'
import { Separator } from '@ui/separator'
import { actions as mapActions } from '@redux/map'
import { RootState } from '@redux/reducers'

export function MapControlsCenterRight(): JSX.Element {
  const [isNavigationLoading, setNavigationLoading] = useState(false)

  const dispatch = useDispatch()
  const zoom: number = useSelector((state: RootState) => state.map.zoom)

  const setZoom = (zoom: number) => dispatch(mapActions.setZoom(zoom))
  const handleZoomIn = () => setZoom(zoom + 1)
  const handleZoomOut = () => setZoom(zoom - 1)
  const setMapCenter = (lng: number, lat: number) => dispatch(mapActions.setCenter({ lng, lat }))

  const handleNavigationClick = (): void => {
    setNavigationLoading(true)
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition((position) => {
        const { latitude, longitude } = position.coords
        setMapCenter(longitude, latitude)
        setNavigationLoading(false)
      })
    }
  }

  return (
    <>
      <ControlGroup direction="vertical">
        <Control
          iconType={IconHubTypes.SVG}
          iconName={iconHubList.ACTION_PLUS}
          onClick={handleZoomIn}
        />
        <Separator position="top" theme="action" />
        <Control
          iconType={IconHubTypes.SVG}
          iconName={iconHubList.ACTION_MINUS}
          onClick={handleZoomOut}
        />
      </ControlGroup>
      <Control
        iconType={IconHubTypes.SVG}
        iconName={iconHubList.ACTION_COMPASS}
        loading={isNavigationLoading}
        onClick={handleNavigationClick}
        is={'location'}
      />
    </>
  )
}
