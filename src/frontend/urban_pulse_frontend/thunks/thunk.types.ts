import { Dispatch } from '@reduxjs/toolkit'
import { RootState } from '@redux/reducers'

export type RejectError = string

export type ThunkApi<RejectValue = RejectError | null | undefined> = {
  state: RootState
  dispatch: Dispatch
  rejectValue: RejectValue
}
