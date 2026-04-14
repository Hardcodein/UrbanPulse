import type maplibregl from 'maplibre-gl'

interface Window {
  __MAP: maplibregl.Map | null
}
