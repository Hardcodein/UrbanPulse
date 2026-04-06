import { client } from '@network/client'
import * as NetworkTypes from '@network/types'
import { Types as SearchTypes } from '@redux/search'

export const search = {
  get: async (
    params: NetworkTypes.SearchParams
  ): Promise<NetworkTypes.ApiResult<SearchTypes.SearchResult[]>> => {
    const response = await client.rest.get('/search', { params })
    return await response.data
  },
}
