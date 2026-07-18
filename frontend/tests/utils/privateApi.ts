import type { UserPublic } from "../../src/client"

const apiBaseUrl = process.env.VITE_API_URL

if (!apiBaseUrl) {
  throw new Error("Environment variable VITE_API_URL is undefined")
}

export const createUser = async ({
  email,
  password,
  fullName = "Test User",
}: {
  email: string
  password: string
  fullName?: string
}) => {
  const response = await fetch(`${apiBaseUrl}/api/v1/private/users/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
      is_verified: true,
      full_name: fullName,
    }),
  })

  if (!response.ok) {
    throw new Error(`Unable to create test user: HTTP ${response.status}`)
  }

  return (await response.json()) as UserPublic
}
