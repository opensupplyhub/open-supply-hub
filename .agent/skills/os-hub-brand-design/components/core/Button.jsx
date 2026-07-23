import React from 'react';

/** Pill button in the OSH deck CTA style (e.g. "GET PRICING"). */
export function Button({ variant = 'primary', size = 'md', children, ...rest }) {
  const palettes = {
    primary: { background: 'var(--osh-off-black)', color: 'var(--osh-off-white)', border: '1.5px solid var(--osh-off-black)' },
    accent: { background: 'var(--osh-purple)', color: 'var(--osh-off-white)', border: '1.5px solid var(--osh-purple)' },
    outline: { background: 'transparent', color: 'var(--osh-off-black)', border: '1.5px solid var(--osh-off-black)' },
    inverse: { background: 'var(--osh-off-white)', color: 'var(--osh-off-black)', border: '1.5px solid var(--osh-off-white)' },
  };
  const sizes = {
    sm: { fontSize: 12, padding: '8px 20px' },
    md: { fontSize: 14, padding: '12px 28px' },
    lg: { fontSize: 16, padding: '16px 36px' },
  };
  return (
    <button
      style={{
        fontFamily: 'var(--font-body)',
        fontWeight: 700,
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        borderRadius: 'var(--radius-pill)',
        cursor: 'pointer',
        ...palettes[variant],
        ...sizes[size],
      }}
      onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.85'; }}
      onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}
      {...rest}
    >
      {children}
    </button>
  );
}
