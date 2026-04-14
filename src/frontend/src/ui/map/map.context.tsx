import maplibregl from 'maplibre-gl'
import { createContext, ReactNode } from 'react'

type ProviderProps = {
  map: maplibregl.Map | null
  children: ReactNode
}

type ContextProps = maplibregl.Map | null

export const MapContext = createContext<ContextProps>(null)

export function MapProvider({ map, children }: ProviderProps): JSX.Element {
  return <MapContext.Provider value={map}>{children}</MapContext.Provider>
}
