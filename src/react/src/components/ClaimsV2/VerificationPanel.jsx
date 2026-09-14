import React from 'react';

import {
    scoreChip,
    organizationRowStatus,
    CHIP_STATUS,
} from './verificationUtils';
import styles from './styles';

/*
 * Compact verification panel (OSDEV-3356, SPEC.md §5a). Each row shows
 * ONE value with a small provenance tag — whether it comes from the OS
 * Hub profile or from the claimant — because the rows are not all
 * two-sided: profile rows (Name, Address) are checked against the
 * claimant's documents, claimant rows (Person, Email) have no profile
 * counterpart at all. Where a real cross-check pair exists, a muted
 * comparison line shows the other side (the Account row's profile
 * name; the Name row's claimant-submitted native-language name).
 * Statuses are advisory; the documents are in the evidence viewer.
 */

const CHIP_STYLES = Object.freeze({
    [CHIP_STATUS.PASS]: 'verificationChipPass',
    [CHIP_STATUS.CHECK]: 'verificationChipCheck',
    [CHIP_STATUS.NONE]: 'verificationChipNone',
});

export const PROVENANCE = Object.freeze({
    PROFILE: 'OS Hub profile',
    CLAIMANT: 'Claimant',
});

function Row({ label, value, provenance, counterpart, chip, footnote }) {
    return (
        <div style={styles.verificationRow}>
            <div style={styles.verificationLabel}>{label}</div>
            <div style={styles.verificationValue}>
                <span style={styles.provenanceTag}>{provenance}</span>
                <div>{value || '—'}</div>
                {counterpart && counterpart.value && (
                    <div style={styles.counterpartLine}>
                        {counterpart.label}: {counterpart.value}
                    </div>
                )}
            </div>
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
    const emailValue = [detail.email, detail.website]
        .filter(Boolean)
        .join(' · ');

    return (
        <section aria-label="Verification">
            <div style={styles.sectionLabel}>Verification</div>
            <div style={styles.verificationTable}>
                <Row
                    label="Name"
                    value={facility.name}
                    provenance={PROVENANCE.PROFILE}
                    counterpart={{
                        label: 'Claimant (native language)',
                        value: detail.facility_name_native_language,
                    }}
                    chip={scoreChip(review, 'name')}
                />
                <Row
                    label="Claimant Account"
                    value={detail.company_name}
                    provenance={PROVENANCE.CLAIMANT}
                    counterpart={{
                        label: 'OS Hub profile',
                        value: facility.name,
                    }}
                    chip={organizationRowStatus(
                        review,
                        facility.name,
                        detail.company_name,
                    )}
                    footnote="Account name is claimant-stated registration data."
                />
                <Row
                    label="Address"
                    value={facility.address}
                    provenance={PROVENANCE.PROFILE}
                    chip={scoreChip(review, 'address')}
                />
                <Row
                    label="Person & title"
                    value={personValue}
                    provenance={PROVENANCE.CLAIMANT}
                    chip={scoreChip(review, 'person')}
                />
                <Row
                    label="Claimant Email"
                    value={emailValue}
                    provenance={PROVENANCE.CLAIMANT}
                    chip={scoreChip(review, 'affiliation')}
                />
            </div>
            <div style={styles.verificationFootnote}>
                Statuses are advisory — every value is checked against the
                claimant&apos;s documents, which are in the evidence viewer
                below.
            </div>
        </section>
    );
}
