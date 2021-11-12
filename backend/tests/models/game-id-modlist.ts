import Ajv from "ajv";
const ajv = new Ajv();

const ModSchema = {
  type: "object",
  properties: {
    required: { type: "boolean" },
    link: { type: "string" },
    icon: { type: "string" },
    replaces: { type: "string" },
    lastModified: { type: "number" },
    files: { type: "array", items: { type: "object" }}
  },
  required: ["required", "lastModified", "files"],
  additionalProperties: false
}

export const validateMod = ajv.compile(ModSchema);