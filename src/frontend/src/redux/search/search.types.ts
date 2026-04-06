import { EntityState } from '@reduxjs/toolkit'
import * as ThunksTypes from '@thunks/thunk.types'

export type SearchResult = {
  id: string
  name: string
}

export type Meta = {
  fetching: boolean
  error: ThunksTypes.RejectError | null
}

export type State = EntityState<SearchResult> & {
  meta: Meta
}
