import React, { useState } from 'react';
import isURL from 'validator/lib/isURL';

import styles from './styles';
import ProfileVisibilityNote from '../Shared/ProfileVisibilityNote/ProfileVisibilityNote';

/*
 * Claimant-submitted details (OSDEV-3356): everything else the
 * claimant provided on the claim form that verification doesn't
 * surface — evidence for judgement calls (LinkedIn especially), shown
 * compactly and only when present.
 */

// isPubliclyVisible is set only on the rows whose value the claimant can
// choose to show on the production location profile (OSDEV-2680).
function DetailRow({ label, value, isPubliclyVisible }) {
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
                {isPubliclyVisible !== undefined && (
                    <ProfileVisibilityNote
                        isPubliclyVisible={isPubliclyVisible}
                    />
                )}
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
            Boolean(detail.facility_website_publicly_visible),
        ],
        [
            'Production location phone',
            detail.facility_phone_number,
            Boolean(detail.facility_phone_number_publicly_visible),
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
                rows.map(([label, value, isPubliclyVisible]) => (
                    <DetailRow
                        key={label}
                        label={label}
                        value={value}
                        isPubliclyVisible={isPubliclyVisible}
                    />
                ))}
        </div>
    );
}
