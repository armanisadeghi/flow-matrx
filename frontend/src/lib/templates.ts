const TEMPLATE_REGEX = /\{\{([^}]+)\}\}/g;

export interface TemplateRef {
  raw: string;
  stepId: string;
  field: string;
}

export function parseTemplateRefs(value: string): TemplateRef[] {
  const refs: TemplateRef[] = [];
  let match: RegExpExecArray | null;

  while ((match = TEMPLATE_REGEX.exec(value)) !== null) {
    const inner = match[1].trim();
    const [stepId, ...fieldParts] = inner.split(".");
    refs.push({ raw: match[0], stepId, field: fieldParts.join(".") });
  }

  return refs;
}

export function hasTemplateRefs(value: string): boolean {
  return TEMPLATE_REGEX.test(value);
}
