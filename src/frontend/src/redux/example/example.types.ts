export type State = {
  foo: string
  bar: number
}

export type OnlyFoo = Pick<State, 'foo'>
export type OnlyBar = Pick<State, 'bar'>
