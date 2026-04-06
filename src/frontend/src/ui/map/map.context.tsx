import mapboxgl from 'mapbox-gl'
import { createContext, ReactNode } from 'react'

type ProviderProps = {
  map: mapboxgl.Map | null
  children: ReactNode
}

type ContextProps = mapboxgl.Map | null

export const MapContext = createContext<ContextProps>(null)

export function MapProvider({ map, children }: ProviderProps): JSX.Element {
  return <MapContext.Provider value={map}>{children}</MapContext.Provider>
}
