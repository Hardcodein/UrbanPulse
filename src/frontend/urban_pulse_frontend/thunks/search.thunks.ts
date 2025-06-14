import { Api } from '@network/api'
import * as NetworkTypes from '@network/types'
import { createAsyncThunk } from '@reduxjs/toolkit'
import cuid from 'cuid'
import { Types as SearchTypes } from '@redux/search'
import { ThunkApi } from './thunk.types'

export const getSearch = createAsyncThunk<
  SearchTypes.SearchResult[],
  NetworkTypes.SearchParams,
  ThunkApi
>('search/get', async (params, api) => {
  try {
    const result = await Api.v1.search.get(params)
    return result?.results?.map((item) => ({ ...item, id: cuid() }))
  } catch (error) {
    // TODO remove ts ignore
    // @ts-ignore
    return api.rejectWithValue(error.message)
  }
})
