import { describe, expect, it, vi } from "vitest"

import { JobsService } from "@/client"
import {
  admissionCapacityQueryKey,
  getAdmissionCapacityQueryOptions,
} from "./queries"

describe("course admission capacity query", () => {
  it("uses the generated owner-scoped capacity endpoint", async () => {
    const capacitySpy = vi
      .spyOn(JobsService, "readAdmissionCapacity")
      .mockResolvedValue({ available_jobs: 8 } as never)
    const options = getAdmissionCapacityQueryOptions()

    expect(admissionCapacityQueryKey).toEqual(["jobs", "admission-capacity"])
    await options.queryFn?.({} as never)
    expect(capacitySpy).toHaveBeenCalledOnce()
  })
})
