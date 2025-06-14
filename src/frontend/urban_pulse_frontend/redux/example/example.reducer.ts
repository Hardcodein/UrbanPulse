import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import * as Types from './example.types'

const initialState: Types.State = {
  foo: '',
  bar: 0,
}

const exampleSlice = createSlice({
  name: 'example',
  initialState,
  reducers: {
    actionName1: (state, action: PayloadAction<Types.OnlyBar>) => {
      state.bar = action.payload.bar
    },
    actionName2: (state, action: PayloadAction<Types.OnlyFoo>) => {
      state.foo = action.payload.foo
    },
  },
})

export const { reducer, actions } = exampleSlice
