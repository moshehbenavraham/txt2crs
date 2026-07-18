import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import type { UserConfig } from "@hey-api/openapi-ts"

const frontendRoot = dirname(fileURLToPath(import.meta.url))

export default {
  input: resolve(frontendRoot, "openapi.json"),
  output: {
    path: resolve(frontendRoot, "src/client"),
    postProcess: ["biome:format"],
  },

  plugins: [
    {
      name: "@hey-api/client-fetch",
      throwOnError: true,
    },
    {
      name: "@hey-api/sdk",
      operations: {
        strategy: "byTags",
        methods: "static",
        containerName: "{{name}}Service",
        nesting: (operation) => [
          operation.operationId?.split("-").at(-1) ?? operation.id,
        ],
      },
      paramsStructure: "grouped",
      responseStyle: "data",
    },
    {
      name: "@hey-api/schemas",
      type: "json",
    },
  ],
} satisfies UserConfig
