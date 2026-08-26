import { randomBytes } from "node:crypto"

/**
 * Builds a random lowercase alphanumeric token of the requested length.
 *
 * We deliberately use Node's cryptographically secure `randomBytes` instead of
 * `Math.random()`. Even though these values only ever feed throwaway test
 * fixtures, some of them become account passwords, and static analysis (and any
 * human reader) should never have to guess whether a weak generator leaked into
 * something security relevant.
 */
const randomToken = (length: number) =>
  randomBytes(length).toString("base64url").toLowerCase().slice(0, length)

export const randomEmail = () => `test_${randomToken(6)}@example.com`

export const randomTeamName = () => `Team ${randomToken(6)}`

export const randomPassword = () => `Test!${randomToken(12)}`

export const randomItemTitle = () => `Item ${randomToken(8)}`

export const randomItemDescription = () => `Description ${randomToken(12)}`

export const slugify = (text: string) =>
  text
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w-]+/g, "")
