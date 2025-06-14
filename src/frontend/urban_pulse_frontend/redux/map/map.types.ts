export type Center = {
  lat: number
  lng: number
}

export type Viewport = Center & {
  zoom: number
}

export type State = Viewport & {
  style: string
  mod: string
  dragging: boolean
}
