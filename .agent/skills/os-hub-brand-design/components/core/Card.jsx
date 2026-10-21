import React from 'react';

/** Flat content card — white surface, 16px radius, optional off-black keyline. No shadow. */
export function Card({ tone = 'white', keyline = false, padding = 32, children, style, ...rest }) {
  const tones = {
    white: { background: 'var(--surface-card)' },
    offwhite: { background: 'var(--surface-page)' },
    dark: { background: 'var(--surface-page-dark)', color: 'var(--text-inverse)' },
    yellow: { background: 'var(--osh-yellow)' },
    greenTint: { background: 'var(--osh-green-tint)' },
  };
  return (
    <div
      style={{
        borderRadius: 'var(--radius-card)',
        border: keyline ? 'var(--border-keyline)' : 'none',
        padding,
        fontFamily: 'var(--font-body)',
        ...tones[tone],
        ...style,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}
