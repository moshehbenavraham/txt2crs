import type { QueryClient } from "@tanstack/react-query"

import type { ApiError } from "@/lib/api-error"

export const ACCESS_TOKEN_STORAGE_KEY = "access_token"
export const CURRENT_USER_QUERY_KEY = ["currentUser"] as const

const isCurrentUserRequest = (url: string) => {
  return url.includes("/users/me")
}

export const shouldInvalidateSession = (error: ApiError) => {
  const isUnauthorized = error.status === 401
  const isStaleCurrentUserLookup =
    error.status === 404 && isCurrentUserRequest(error.url)

  return isUnauthorized || isStaleCurrentUserLookup
}

export type TokenStorageAdapter = Pick<
  Storage,
  "getItem" | "setItem" | "removeItem"
>
export type TokenStorageAdapters = {
  session: TokenStorageAdapter | null
  local: TokenStorageAdapter | null
}

const getDefaultTokenStorages = (): TokenStorageAdapters => {
  if (typeof window === "undefined") {
    return {
      session: null,
      local: null,
    }
  }

  return {
    session: window.sessionStorage,
    local: window.localStorage,
  }
}

export const getAccessToken = (
  storages: TokenStorageAdapters = getDefaultTokenStorages(),
) => {
  const sessionToken =
    storages.session?.getItem(ACCESS_TOKEN_STORAGE_KEY) ?? null
  if (sessionToken) {
    return sessionToken
  }

  const legacyLocalToken =
    storages.local?.getItem(ACCESS_TOKEN_STORAGE_KEY) ?? null
  if (legacyLocalToken) {
    // Migrate legacy persistent tokens into session-scoped storage.
    storages.session?.setItem(ACCESS_TOKEN_STORAGE_KEY, legacyLocalToken)
    storages.local?.removeItem(ACCESS_TOKEN_STORAGE_KEY)
  }

  return legacyLocalToken
}

export const hasAccessToken = (
  storages: TokenStorageAdapters = getDefaultTokenStorages(),
) => {
  return getAccessToken(storages) !== null
}

export const setAccessToken = (
  token: string,
  storages: TokenStorageAdapters = getDefaultTokenStorages(),
) => {
  storages.session?.setItem(ACCESS_TOKEN_STORAGE_KEY, token)
  storages.local?.removeItem(ACCESS_TOKEN_STORAGE_KEY)
}

export const removeAccessToken = (
  storages: TokenStorageAdapters = getDefaultTokenStorages(),
) => {
  storages.session?.removeItem(ACCESS_TOKEN_STORAGE_KEY)
  storages.local?.removeItem(ACCESS_TOKEN_STORAGE_KEY)
}

export const resetAuthQueryCache = (queryClient: QueryClient) => {
  queryClient.clear()
}

export const clearAuthSession = (
  queryClient: QueryClient,
  storages: TokenStorageAdapters = getDefaultTokenStorages(),
) => {
  resetAuthQueryCache(queryClient)
  removeAccessToken(storages)
}
