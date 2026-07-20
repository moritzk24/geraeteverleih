import { HttpErrorResponse } from '@angular/common/http';

/**
 * FastAPI returns `detail` as a plain string for HTTPException (404/409/…),
 * but as an array of pydantic validation error objects for 422 responses.
 * Normalize both shapes into one readable message.
 */
export function extractErrorMessage(err: unknown, fallback: string): string {
  const detail = err instanceof HttpErrorResponse ? err.error?.detail : undefined;

  if (typeof detail === 'string') {
    return detail;
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((e) => (typeof e?.msg === 'string' ? e.msg.replace(/^Value error,\s*/, '') : null))
      .filter((msg): msg is string => !!msg);
    if (messages.length > 0) {
      return messages.join('; ');
    }
  }

  return fallback;
}
