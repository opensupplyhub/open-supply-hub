import React from 'react';

/** Small solid tag/chip for stakeholder groups and category labels. */
export function Tag({ color = 'yellow', children, ...rest }) {
  const fills = {
    yellow: { background: 'var(--osh-yellow)', color: 'var(--osh-off-black)' },
    purple: { background: 'var(--osh-purple)', color: 'var(--osh-off-white)' },
    green: { background: 'var(--osh-green)', color: 'var(--osh-off-black)' },
    pink: { background: 'var(--osh-pink)', color: 'var(--osh-off-black)' },
    dark: { background: 'var(--osh-off-black)', color: 'var(--osh-off-white)' },
    outline: { background: 'transparent', color: 'var(--osh-off-black)', border: '1.5px solid var(--osh-off-black)' },
  };
  return (
    <span
      style={{
        display: 'inline-block',
        fontFamily: 'var(--font-body)',
        fontWeight: 700,
        fontSize: 13,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        padding: '5px 14px',
        borderRadius: 'var(--radius-pill)',
        ...fills[color],
      }}
      {...rest}
    >
      {children}
    </span>
  );
}
