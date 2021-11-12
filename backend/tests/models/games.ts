import Ajv from "ajv";
const ajv = new Ajv();

const GameSchema = {
  type: "object",
  properties: {
    altname: { type: "string" },
    icon: { type: "string" },
    lastModified: { type: "number" },
    desiredFilesInPath: { type: "array", items: { type: "string" }}
  },
  required: ["altname", "icon", "lastModified"],
  additionalProperties: false
}

export const validateGame = ajv.compile(GameSchema);