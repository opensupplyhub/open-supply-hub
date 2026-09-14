import React from 'react';

import {
    scoreChip,
    organizationRowStatus,
    CHIP_STATUS,
} from './verificationUtils';
import styles from './styles';

/*
 * Compact verification panel (OSDEV-3356, SPEC.md §5a): five rows,
 * each pairing the OS Hub profile value and the claimant-submitted
 * value side by side for a glance check, with the automated review's
 * tier-1 status beside them. Statuses are advisory; the documents
 * themselves are in the evidence viewer.
 */

const CHIP_STYLES = Object.freeze({
    [CHIP_STATUS.PASS]: 'verificationChipPass',
    [CHIP_STATUS.CHECK]: 'verificationChipCheck',
    [CHIP_STATUS.NONE]: 'verificationChipNone',
});

function Row({ label, profileValue, submittedValue, chip, footnote }) {
    return (
        <div style={styles.verificationRow}>
            <div style={styles.verificationLabel}>{label}</div>
            <div style={styles.verificationValue}>{profileValue || '—'}</div>
            <div style={styles.verificationValue}>{submittedValue || '—'}</div>
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
                <div
                    style={{
                        ...styles.verificationRow,
                        ...styles.verificationHeadRow,
                    }}
                >
                    <div style={styles.verificationLabel} />
                    <div style={styles.verificationValue}>OS Hub profile</div>
                    <div style={styles.verificationValue}>
                        Claimant submitted
                    </div>
                    <div style={styles.verificationStatus}>
                        Automated review
                    </div>
                </div>
                <Row
                    label="Name"
                    profileValue={facility.name}
                    submittedValue={detail.facility_name_native_language}
                    chip={scoreChip(review, 'name')}
                />
                <Row
                    label="Claimant Account"
                    profileValue={facility.name}
                    submittedValue={detail.company_name}
                    chip={organizationRowStatus(
                        review,
                        facility.name,
                        detail.company_name,
                    )}
                    footnote="Account name is claimant-stated registration data."
                />
                <Row
                    label="Address"
                    profileValue={facility.address}
                    submittedValue={null}
                    chip={scoreChip(review, 'address')}
                />
                <Row
                    label="Person & title"
                    profileValue={null}
                    submittedValue={personValue}
                    chip={scoreChip(review, 'person')}
                />
                <Row
                    label="Claimant Email"
                    profileValue={null}
                    submittedValue={emailValue}
                    chip={scoreChip(review, 'affiliation')}
                />
            </div>
            <div style={styles.verificationFootnote}>
                Statuses are advisory — the documents themselves are in the
                evidence viewer. “—” means there is nothing on that side to
                compare.
            </div>
        </section>
    );
}
