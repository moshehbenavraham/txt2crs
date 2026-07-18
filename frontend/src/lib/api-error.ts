type ValidationIssue = {
  msg?: string
}

type ProblemDetails = {
  detail?: string | ValidationIssue[]
  title?: string
}

const isProblemDetails = (value: unknown): value is ProblemDetails => {
  return typeof value === "object" && value !== null
}

export const getApiErrorMessage = (error: unknown): string => {
  if (error instanceof ApiError) {
    return getApiErrorMessage(error.body)
  }

  if (isProblemDetails(error)) {
    if (Array.isArray(error.detail) && error.detail.length > 0) {
      return error.detail[0]?.msg ?? "Something went wrong."
    }

    if (typeof error.detail === "string") {
      return error.detail
    }

    if (typeof error.title === "string") {
      return error.title
    }
  }

  if (error instanceof Error) {
    return error.message
  }

  if (typeof error === "string" && error) {
    return error
  }

  return "Something went wrong."
}

export class ApiError extends Error {
  readonly body: unknown
  readonly status: number
  readonly url: string

  constructor({
    body,
    status,
    url,
  }: {
    body: unknown
    status: number
    url: string
  }) {
    super(getApiErrorMessage(body))
    this.name = "ApiError"
    this.body = body
    this.status = status
    this.url = url
  }
}

export const createApiError = (
  error: unknown,
  response?: Response,
  request?: Request,
) => {
  if (error instanceof ApiError) {
    return error
  }

  return new ApiError({
    body: error,
    status: response?.status ?? 0,
    url: request?.url ?? "",
  })
}
