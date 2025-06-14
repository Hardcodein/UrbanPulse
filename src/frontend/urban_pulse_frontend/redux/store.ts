import { configureStore, getDefaultMiddleware, EnhancedStore, AnyAction } from '@reduxjs/toolkit'
import { useMemo } from 'react'
import {
  persistStore,
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
  Persistor,
} from 'redux-persist'
import createWebStorage from 'redux-persist/lib/storage/createWebStorage'
import { reducers, RootState } from './reducers'

type Store = EnhancedStore<RootState, AnyAction>
let store: Store | undefined

const isProd = process.env.NODE_ENV === 'production'

const createNoopStorage = () => {
  return {
    getItem() {
      return Promise.resolve(null)
    },
    setItem(_key: string, value: string) {
      return Promise.resolve(value)
    },
    removeItem() {
      return Promise.resolve()
    },
  }
}

const storage = typeof window !== 'undefined' ? createWebStorage('local') : createNoopStorage()

const persistConfig = {
  key: 'root',
  storage: storage,
  version: 1,
  whitelist: ['history'],
}

const persistedReducer = persistReducer(persistConfig, reducers)

function initStore(preloadedState = {}) {
  return configureStore({
    reducer: persistedReducer,
    devTools: !isProd,
    preloadedState,
    middleware: getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
  })
}

export const initializeStore = (preloadedState: Record<string, unknown>): Store => {
  let _store = store ?? initStore(preloadedState)

  // After navigating to a page with an initial Redux state, merge that state
  // with the current state in the store, and create a new store
  if (preloadedState && store) {
    _store = initStore({
      ...store.getState(),
      ...preloadedState,
    })
    // Reset the current store
    store = undefined
  }

  // For SSG and SSR always create a new store
  if (typeof window === 'undefined') return _store
  // Create the store once in the client
  if (!store) store = _store

  return _store
}

export function useStore(
  initialState: Record<string, unknown>
): {
  store: Store
  persistor: Persistor
} {
  const store = useMemo(() => initializeStore(initialState), [initialState])
  const persistor = persistStore(store as Store)
  return { store, persistor }
}
