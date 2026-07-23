/**
 * Pill CTA button in the OSH deck style.
 */
export interface ButtonProps {
  /** Visual style */
  variant?: 'primary' | 'accent' | 'outline' | 'inverse';
  size?: 'sm' | 'md' | 'lg';
  children?: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}
