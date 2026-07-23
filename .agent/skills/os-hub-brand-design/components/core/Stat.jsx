import React from 'react';

/** Big-number stat callout, e.g. "2,500,000+ / Production locations listed". */
export function Stat({ value, label, sublabel, color = 'var(--osh-purple)', align = 'center', ...rest }) {
  return (
    <div style={{ textAlign: align, fontFamily: 'var(--font-body)' }} {...rest}>
      <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 72, lineHeight: 0.9, color }}>{value}</div>
      <div style={{ fontWeight: 700, fontSize: 20, marginTop: 8, color: 'var(--text-body)' }}>{label}</div>
      {sublabel ? <div style={{ fontSize: 15, marginTop: 4, color: 'var(--text-muted)' }}>{sublabel}</div> : null}
    </div>
  );
}
