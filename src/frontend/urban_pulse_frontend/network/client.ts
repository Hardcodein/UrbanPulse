import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import * as Qs from 'qs'

class AxiosHelper {
  constructor() {
    this.rest = axios.create()
  }

  public rest: AxiosInstance

  public init() {
    this.rest = this.createAxiosInstance()
  }

  public createAxiosInstance() {
    const axiosConfig: AxiosRequestConfig = {
      paramsSerializer: function (params) {
        return Qs.stringify(params, { arrayFormat: 'comma' })
      },
    }
    return axios.create(axiosConfig)
  }
}

export const client = new AxiosHelper()
