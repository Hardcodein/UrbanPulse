import { combineReducers } from 'redux'
import { reducer as example } from './example'
import { reducer as map } from './map'
import { reducer as search } from './search'

export const reducers = combineReducers({
  example,
  search,
  map,
})

export type RootState = ReturnType<typeof reducers>
