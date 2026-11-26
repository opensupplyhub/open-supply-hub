/** Big-number stat callout used on community/stats slides. */
export interface StatProps {
  /** The number, e.g. "2,500,000+" */
  value: string;
  /** Bold one-line label */
  label: string;
  /** Optional muted second line */
  sublabel?: string;
  /** Number color (token) */
  color?: string;
  align?: 'left' | 'center';
}
