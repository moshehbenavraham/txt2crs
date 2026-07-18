import { spawnSync } from "node:child_process"
import { readFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..")
const executable = process.platform === "win32" ? "npx.cmd" : "npx"
const packageJson = JSON.parse(
  readFileSync(resolve(frontendRoot, "package.json"), "utf8"),
)
const generatorVersion = packageJson.devDependencies?.["@hey-api/openapi-ts"]

if (
  typeof generatorVersion !== "string" ||
  !/^\d+\.\d+\.\d+$/.test(generatorVersion)
) {
  throw new Error(
    "@hey-api/openapi-ts must use an exact version in devDependencies",
  )
}

// openapi-ts 0.99 imports the legacy TypeScript compiler API. TypeScript 7 is
// the application compiler but no longer exports that API, so run codegen in an
// isolated exact-version tool environment until openapi-ts supports TypeScript 7.
const result = spawnSync(
  executable,
  [
    "--yes",
    "--package=typescript@5.9.3",
    `--package=@hey-api/openapi-ts@${generatorVersion}`,
    "--",
    "openapi-ts",
    "--file",
    resolve(frontendRoot, "openapi-ts.config.ts"),
  ],
  {
    cwd: tmpdir(),
    env: process.env,
    stdio: "inherit",
  },
)

if (result.error) {
  throw result.error
}

process.exit(result.status ?? 1)
