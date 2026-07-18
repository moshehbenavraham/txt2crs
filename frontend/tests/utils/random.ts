export const randomEmail = () =>
  `test_${Math.random().toString(36).substring(7)}@example.com`

export const randomTeamName = () =>
  `Team ${Math.random().toString(36).substring(7)}`

export const randomPassword = () =>
  `Test!${Math.random().toString(36).substring(2, 14)}`

export const randomItemTitle = () =>
  `Item ${Math.random().toString(36).substring(2, 10)}`

export const randomItemDescription = () =>
  `Description ${Math.random().toString(36).substring(2, 14)}`

export const slugify = (text: string) =>
  text
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^\w-]+/g, "")
