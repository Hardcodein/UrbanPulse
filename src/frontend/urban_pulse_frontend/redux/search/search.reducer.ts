import { createSlice, createEntityAdapter } from '@reduxjs/toolkit'
import { getSearch } from '@thunks/search.thunks'
import * as Types from './search.types'

export const adapter = createEntityAdapter<Types.SearchResult>({
  selectId: (item) => item.id,
})

const getInitialState = (): Types.State =>
  adapter.getInitialState({
    meta: {
      fetching: false,
      error: null,
    },
  })

const suggestSlice = createSlice({
  name: 'search',
  initialState: getInitialState(),
  reducers: {
    clear: (state) => {
      Object.assign(state, getInitialState())
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getSearch.pending, (state) => {
        state.meta.fetching = true
      })
      .addCase(getSearch.fulfilled, (state, action) => {
        state.meta.fetching = false
        state.meta.error = null
        adapter.setAll(state, action.payload)
      })
      .addCase(getSearch.rejected, (state, action) => {
        state.meta.fetching = false
        state.meta.error = action.payload || null
      })
  },
})

export const { reducer, actions } = suggestSlice
