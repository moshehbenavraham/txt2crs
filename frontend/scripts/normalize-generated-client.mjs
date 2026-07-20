import { readFileSync, writeFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

// openapi-ts 0.99 emits one smart apostrophe in path-serializer prose. Biome
// first converts the surrounding generated string to double quotes; replacing
// the apostrophe afterward is therefore both valid TypeScript and ASCII. This
// separate final step avoids turning the generator's initial single-quoted
// string into invalid syntax before Biome parses it.
const frontendRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..")
const generatedPathSerializer = resolve(
  frontendRoot,
  "src/client/core/pathSerializer.gen.ts",
)
const generatedPathSerializerSource = readFileSync(
  generatedPathSerializer,
  "utf8",
)
const asciiPathSerializerSource = generatedPathSerializerSource.replaceAll(
  "\u2019",
  "'",
)

if (asciiPathSerializerSource !== generatedPathSerializerSource) {
  writeFileSync(generatedPathSerializer, asciiPathSerializerSource, "utf8")
}
