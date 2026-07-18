import { getApiErrorMessage } from "./lib/api-error"

export const handleError = function (
  this: (msg: string) => void,
  err: unknown,
) {
  const errorMessage = getApiErrorMessage(err)
  this(errorMessage)
}

export const getInitials = (name: string): string => {
  return name
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
}
