/** Flat content card — no shadows, separation by color or keyline. */
export interface CardProps {
  /** Surface fill */
  tone?: 'white' | 'offwhite' | 'dark' | 'yellow' | 'greenTint';
  /** Thin off-black border */
  keyline?: boolean;
  /** Inner padding in px */
  padding?: number;
  children?: React.ReactNode;
}
