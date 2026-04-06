import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { Mods, Styles } from '@redux/map/map.const'
import * as Types from './map.types'

const pos = {
  spb: {
    lng: 30.3141,
    lat: 59.9386,
    zoom: 11,
  },
}

const mapSlice = createSlice({
  name: 'map',
  initialState: {
    lng: pos.spb.lng,
    lat: pos.spb.lat,
    zoom: pos.spb.zoom,
    style: Styles.MAIN,
    mod: Mods.DEFAULT,
    dragging: false,
  } as Types.State,
  reducers: {
    setCenter: (state, action: PayloadAction<Types.Center>) => {
      Object.assign(state, action.payload)
    },
    setZoom: (state, action: PayloadAction<number>) => {
      state.zoom = action.payload
    },
    setMod: (state, action: PayloadAction<string>) => {
      state.mod = action.payload
    },
    setViewport: (state, action: PayloadAction<Types.Viewport>) => {
      Object.assign(state, action.payload)
    },
    setStyle: (state, action: PayloadAction<string>) => {
      state.style = action.payload
    },
    setDragging: (state, action: PayloadAction<boolean>) => {
      state.dragging = action.payload
    },
  },
})

export const { reducer, actions } = mapSlice
