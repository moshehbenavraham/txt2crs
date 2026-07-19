import { describe, expect, it, vi } from "vitest"

import { SystemService } from "@/client"
import {
  getSystemAuthenticationPollingInterval,
  getSystemAuthenticationQueryOptions,
  getSystemReadinessQueryOptions,
  SYSTEM_AUTHENTICATION_QUERY_KEY,
  SYSTEM_READINESS_QUERY_KEY,
} from "./queries"

describe("system setup query contracts", () => {
  it("uses stable feature-scoped cache keys", () => {
    expect(SYSTEM_READINESS_QUERY_KEY).toEqual(["system", "readiness"])
    expect(SYSTEM_AUTHENTICATION_QUERY_KEY).toEqual([
      "system",
      "authentication",
    ])
  })

  it("polls only a waiting ceremony and stops for every terminal state", () => {
    expect(getSystemAuthenticationPollingInterval("waiting_for_user")).toBe(
      1000,
    )
    expect(getSystemAuthenticationPollingInterval("signed_out")).toBe(false)
    expect(getSystemAuthenticationPollingInterval("authenticated")).toBe(false)
    expect(getSystemAuthenticationPollingInterval("failed")).toBe(false)
    expect(getSystemAuthenticationPollingInterval(undefined)).toBe(false)
  })

  it("delegates both query functions to the generated system client", async () => {
    const readinessSpy = vi
      .spyOn(SystemService, "readSystemReadiness")
      .mockResolvedValue({} as never)
    const authenticationSpy = vi
      .spyOn(SystemService, "readSystemAuthenticationStatus")
      .mockResolvedValue({} as never)

    const readinessOptions = getSystemReadinessQueryOptions()
    const authenticationOptions = getSystemAuthenticationQueryOptions()
    await readinessOptions.queryFn?.({} as never)
    await authenticationOptions.queryFn?.({} as never)

    expect(readinessSpy).toHaveBeenCalledOnce()
    expect(authenticationSpy).toHaveBeenCalledOnce()
    expect(authenticationOptions.refetchIntervalInBackground).toBe(false)
  })
})
