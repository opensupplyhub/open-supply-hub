import React from 'react';

/** Uppercase tracked kicker label, e.g. "CASE STUDY", "FEATURES: OS HUB SOLUTIONS". */
export function Eyebrow({ color = 'var(--osh-off-black)', children, ...rest }) {
  return (
    <div
      style={{
        fontFamily: 'var(--font-body)',
        textTransform: 'uppercase',
        letterSpacing: 'var(--tracking-eyebrow)',
        fontWeight: 700,
        fontSize: 'var(--text-eyebrow)',
        color,
      }}
      {...rest}
    >
      {children}
    </div>
  );
}
