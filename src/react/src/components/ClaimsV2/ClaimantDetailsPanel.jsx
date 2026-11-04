import React, { useState } from 'react';
import isURL from 'validator/lib/isURL';

import styles from './styles';

/*
 * Claimant-submitted details (OSDEV-3356): everything else the
 * claimant provided on the claim form that verification doesn't
 * surface — evidence for judgement calls (LinkedIn especially), shown
 * compactly and only when present.
 */

// The claimant's choice of whether a value is shown on the production
// location profile (OSDEV-2680), as a secondary line under the value.
const visibilityNoteStyle = Object.freeze({
    display: 'block',
    fontSize: '14px',
    color: styles.detailKey.color,
});

const profileVisibilityNote = isPubliclyVisible =>
    isPubliclyVisible ? 'Shown on profile' : 'Not shown on profile';

function DetailRow({ label, value, note }) {
    return (
        <div style={styles.matchRow}>
            <span style={styles.detailKey}>{label}</span>
            <span style={styles.matchValue}>
                {isURL(value || '', { require_protocol: true }) ? (
                    <a href={value} target="_blank" rel="noopener noreferrer">
                        {value} ↗
                    </a>
                ) : (
                    value
                )}
                {note && <span style={visibilityNoteStyle}>{note}</span>}
            </span>
        </div>
    );
}

export default function ClaimantDetailsPanel({ detail }) {
    const [collapsed, setCollapsed] = useState(false);

    const rows = [
        ['LinkedIn', detail.linkedin_profile],
        ['Claimant LinkedIn', detail.claimant_linkedin_profile_url],
        ['Website', detail.website],
        [
            'Production location website',
            detail.facility_website,
            profileVisibilityNote(detail.facility_website_publicly_visible),
        ],
        [
            'Production location phone',
            detail.facility_phone_number,
            profileVisibilityNote(
                detail.facility_phone_number_publicly_visible,
            ),
        ],
        ['Sector(s)', (detail.sector || []).join(', ')],
        [
            'Workers',
            detail.facility_workers_count
                ? String(detail.facility_workers_count)
                : null,
        ],
        ['Parent company', detail.facility_parent_company?.name],
        ['Native-language name', detail.facility_name_native_language],
        ['Description', detail.facility_description],
    ].filter(([, value]) => value && String(value).trim() !== '');

    if (rows.length === 0) {
        return null;
    }

    return (
        <div style={styles.profileAnchor}>
            <button
                type="button"
                style={styles.detailToggle}
                onClick={() => setCollapsed(current => !current)}
                aria-expanded={!collapsed}
            >
                <span style={styles.sectionLabel}>
                    Claimant-submitted details ({rows.length})
                    {collapsed ? ' ▸' : ' ▾'}
                </span>
            </button>
            {!collapsed &&
                rows.map(([label, value, note]) => (
                    <DetailRow
                        key={label}
                        label={label}
                        value={value}
                        note={note}
                    />
                ))}
        </div>
    );
}
