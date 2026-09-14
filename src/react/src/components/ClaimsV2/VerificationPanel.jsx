import React from 'react';

import {
    scoreChip,
    organizationRowStatus,
    CHIP_STATUS,
} from './verificationUtils';
import styles from './styles';

/*
 * Compact verification panel (OSDEV-3356, SPEC.md §5a): five rows
 * pairing the OS Hub profile value (comparison baseline) with the
 * automated review's tier-1 status. Statuses are advisory; the
 * documents themselves are in the evidence viewer.
 */

const CHIP_STYLES = Object.freeze({
    [CHIP_STATUS.PASS]: 'verificationChipPass',
    [CHIP_STATUS.CHECK]: 'verificationChipCheck',
    [CHIP_STATUS.NONE]: 'verificationChipNone',
});

function Row({ label, profileValue, chip, footnote }) {
    return (
        <div style={styles.verificationRow}>
            <div style={styles.verificationLabel}>{label}</div>
            <div style={styles.verificationValue}>{profileValue || '—'}</div>
            <div style={styles.verificationStatus}>
                <span
                    style={{
                        ...styles.verificationChip,
                        ...styles[CHIP_STYLES[chip.status]],
                    }}
                >
                    {chip.status === CHIP_STATUS.NONE
                        ? 'Needs your judgement'
                        : chip.text}
                </span>
                {chip.status === CHIP_STATUS.NONE && (
                    <div style={styles.verificationReasoning}>{chip.text}</div>
                )}
                {chip.reasoning && (
                    <div style={styles.verificationReasoning}>
                        {chip.reasoning}
                    </div>
                )}
                {footnote && (
                    <div style={styles.verificationFootnote}>{footnote}</div>
                )}
            </div>
        </div>
    );
}

export default function VerificationPanel({ detail, review }) {
    const facility = detail.facility?.properties || {};
    const personValue = [detail.contact_person, detail.job_title]
        .filter(Boolean)
        .join(' — ');
    const affiliationValue = [detail.email, detail.website]
        .filter(Boolean)
        .join(' · ');

    return (
        <section aria-label="Verification">
            <div style={styles.sectionLabel}>Verification</div>
            <div style={styles.verificationTable}>
                <Row
                    label="Name"
                    profileValue={facility.name}
                    chip={scoreChip(review, 'name')}
                />
                <Row
                    label="Organization"
                    profileValue={detail.company_name}
                    chip={organizationRowStatus(
                        review,
                        facility.name,
                        detail.company_name,
                    )}
                    footnote="Org name is claimant-stated registration data."
                />
                <Row
                    label="Address"
                    profileValue={facility.address}
                    chip={scoreChip(review, 'address')}
                />
                <Row
                    label="Person & title"
                    profileValue={personValue}
                    chip={scoreChip(review, 'person')}
                />
                <Row
                    label="Affiliation"
                    profileValue={affiliationValue}
                    chip={scoreChip(review, 'affiliation')}
                />
            </div>
            <div style={styles.verificationFootnote}>
                Statuses are advisory — the documents themselves are in the
                evidence viewer.
            </div>
        </section>
    );
}
