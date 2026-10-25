import React from 'react';

/** Rounded speech-bubble callout with a solid brand fill and off-black outline. */
export function SpeechBubble({ color = 'yellow', children, style, ...rest }) {
  const fills = {
    yellow: 'var(--osh-yellow)',
    pink: 'var(--osh-pink)',
    green: 'var(--osh-green)',
    white: 'var(--osh-white)',
  };
  return (
    <div style={{ position: 'relative', display: 'inline-block', ...style }} {...rest}>
      <div
        style={{
          background: fills[color],
          border: '2px solid var(--osh-off-black)',
          borderRadius: 28,
          padding: '18px 26px',
          fontFamily: 'var(--font-body)',
          fontWeight: 500,
          fontSize: 18,
          color: 'var(--osh-off-black)',
          lineHeight: 1.35,
        }}
      >
        {children}
      </div>
      <svg width="34" height="26" viewBox="0 0 34 26" style={{ position: 'absolute', left: 34, bottom: -22 }} aria-hidden="true">
        <path d="M2 2 C10 2 22 2 30 2 L14 24 C13 14 8 6 2 2 Z" fill={fills[color]} stroke="var(--osh-off-black)" strokeWidth="2" strokeLinejoin="round"></path>
      </svg>
    </div>
  );
}
