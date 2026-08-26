import { readFileSync } from "node:fs"

import { describe, expect, it } from "vitest"

const nginxConf = readFileSync(
  new URL("../../nginx.conf", import.meta.url),
  "utf8",
)
const frontendDockerfile = readFileSync(
  new URL("../../Dockerfile", import.meta.url),
  "utf8",
)
const deploymentPolicy = readFileSync(
  new URL("../../../docs/deployment-policy.md", import.meta.url),
  "utf8",
)
const selfReferentialApiUrlArgument = [
  "ARG VITE_API_URL=",
  "$",
  "{VITE_API_URL}",
].join("")

describe("frontend nginx security headers", () => {
  it("includes baseline browser hardening directives", () => {
    expect(nginxConf).toContain("add_header Content-Security-Policy")
    expect(nginxConf).toContain("frame-src 'self' blob:")
    expect(nginxConf).toContain("add_header X-Content-Type-Options")
    expect(nginxConf).toContain("add_header X-Frame-Options")
    expect(nginxConf).toContain("add_header Referrer-Policy")
    expect(nginxConf).toContain("add_header Permissions-Policy")
  })
})

describe("frontend container health", () => {
  it("exposes a machine-readable health endpoint", () => {
    expect(nginxConf).toContain("location = /health")
    expect(nginxConf).toContain(
      `return 200 '{"status":"healthy","service":"frontend"}'`,
    )
  })

  it("checks the health endpoint from inside the production image", () => {
    expect(frontendDockerfile).toContain("HEALTHCHECK")
    expect(frontendDockerfile).toContain(
      "curl --fail --silent --show-error http://127.0.0.1/health",
    )
  })

  it("declares the build-time API URL without an undefined self-default", () => {
    expect(frontendDockerfile).toContain("ARG VITE_API_URL\n")
    expect(frontendDockerfile).not.toContain(selfReferentialApiUrlArgument)
  })

  it("documents a portable container baseline and both health probe paths", () => {
    expect(deploymentPolicy).toContain(
      "Docker Compose is the reference deployment source of truth",
    )
    expect(deploymentPolicy).toContain("`/api/v1/utils/health/`")
    expect(deploymentPolicy).toContain("`/health`")
    expect(deploymentPolicy).toContain("hosted container platform")
  })
})
