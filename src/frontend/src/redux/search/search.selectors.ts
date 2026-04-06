import { RootState } from '../reducers'
import { adapter } from './search.reducer'

export const selectors = adapter.getSelectors<RootState>((state) => state.search)
