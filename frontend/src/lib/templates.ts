const TEMPLATE_PATTERN = /\{\{([^}]+)\}\}/g;

export interface TemplateRef {
  raw: string;
  stepId: string;
  field: string;
}

export function parseTemplateRefs(value: string): TemplateRef[] {
  const refs: TemplateRef[] = [];
  // Create a new regex instance per call to avoid stale lastIndex state.
  const regex = new RegExp(TEMPLATE_PATTERN.source, "g");
  let match: RegExpExecArray | null;

  while ((match = regex.exec(value)) !== null) {
    const inner = match[1].trim();
    const [stepId, ...fieldParts] = inner.split(".");
    refs.push({ raw: match[0], stepId, field: fieldParts.join(".") });
  }

  return refs;
}

export function hasTemplateRefs(value: string): boolean {
  return TEMPLATE_PATTERN.test(value);
}
