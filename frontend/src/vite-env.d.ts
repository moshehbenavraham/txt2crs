/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_ENABLE_PUBLIC_SIGNUP?: "true" | "false"
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
