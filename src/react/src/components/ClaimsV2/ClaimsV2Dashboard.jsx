import React, { useState } from 'react';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';

import { useClaimsList, useClaimDetail } from './hooks';
import { deriveClaimStage, CLAIM_STAGES, NOTE_TYPES } from './stageUtils';
import { makeClaimTrackerTicketSearchURL } from './jiraUtils';
import styles from './styles';

/*
 * Claims moderation dashboard v2 — scaffolding shell (OSDEV-3355).
 *
 * Renders the real pending-claims list and a minimal claim workspace:
 * derived stage, note timeline with direction labels (OSDEV-3351),
 * decision record (OSDEV-3352), and the Jira assignment deep-link.
 * The full Queue workspace (verification panel, evidence-beside-composer
 * workbench, templates, J/K navigation) lands with OSDEV-3356 — visual
 * spec: https://claims-moderation-prototype.vercel.app
 */

const NOTE_TAG_LABELS = Object.freeze({
    [NOTE_TYPES.INTERNAL]: 'Internal',
    [NOTE_TYPES.CLAIMANT_MESSAGE]: 'Emailed to claimant',
    [NOTE_TYPES.CLAIMANT_UPDATE]: 'Claimant update',
});

const STAGE_LABELS = Object.freeze({
    [CLAIM_STAGES.NEW]: 'New — needs review',
    [CLAIM_STAGES.AWAITING]: 'Awaiting claimant',
    [CLAIM_STAGES.OVERDUE]: 'Reply overdue — decide',
});

const ageInDays = createdAt =>
    Math.max(
        0,
        Math.floor((Date.now() - new Date(createdAt)) / (24 * 60 * 60 * 1000)),
    );

function ClaimWorkspace({ claimID }) {
    const { detail, fetching, error } = useClaimDetail(claimID);

    if (!claimID) {
        return (
            <Typography variant="body1">
                Select a claim from the queue.
            </Typography>
        );
    }
    if (fetching) {
        return <CircularProgress size={30} />;
    }
    if (error) {
        return <Typography variant="body1">{error}</Typography>;
    }
    if (!detail) {
        return null;
    }

    const stage = deriveClaimStage(detail.notes);
    const facilityName =
        (detail.facility &&
            detail.facility.properties &&
            detail.facility.properties.name) ||
        `Claim #${detail.id}`;
    const statusChange = detail.status_change || {};

    return (
        <div>
            <Typography variant="title" gutterBottom>
                {facilityName}{' '}
                <span style={styles.noteMeta}>Claim #{detail.id}</span>
            </Typography>
            <Typography variant="body1">
                {detail.contact_person}
                {detail.job_title ? ` — ${detail.job_title}` : ''} ·{' '}
                {detail.email}
            </Typography>
            <div style={styles.stageBox}>
                <strong>{STAGE_LABELS[stage.stage]}</strong>
                <div style={styles.noteMeta}>{stage.reason}</div>
            </div>
            {detail.status !== 'PENDING' && (
                <div style={styles.stageBox}>
                    <strong>{detail.status}</strong>
                    {statusChange.status_change_by
                        ? ` by ${statusChange.status_change_by}`
                        : ''}
                    {statusChange.status_change_reason && (
                        <div style={styles.noteMeta}>
                            Emailed to claimant:{' '}
                            {statusChange.status_change_reason}
                        </div>
                    )}
                </div>
            )}
            <Typography variant="body1">
                <a
                    href={makeClaimTrackerTicketSearchURL(detail.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Assignment is managed in Jira — open this claim&apos;s
                    ticket ↗
                </a>
            </Typography>
            <div>
                {(detail.notes || []).map(note => (
                    <div key={note.id} style={styles.noteItem}>
                        <div style={styles.noteMeta}>
                            {note.author} · {note.created_at}
                            <span style={styles.noteTag}>
                                {NOTE_TAG_LABELS[note.note_type] ||
                                    'Internal'}
                            </span>
                        </div>
                        <div>{note.note}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function ClaimsV2Dashboard() {
    const { claims, fetching, error, refetchClaims } = useClaimsList();
    const [selectedClaimID, setSelectedClaimID] = useState(null);

    if (fetching) {
        return <CircularProgress size={50} />;
    }
    if (error) {
        return (
            <div>
                <Typography variant="body1">{error}</Typography>
                <button type="button" onClick={refetchClaims}>
                    Retry
                </button>
            </div>
        );
    }

    return (
        <div style={styles.shell}>
            <nav style={styles.rail} aria-label="Pending claims queue">
                <Typography variant="body1" gutterBottom>
                    {claims.length} pending claim(s)
                </Typography>
                {claims.map(claim => (
                    <button
                        type="button"
                        key={claim.id}
                        style={{
                            ...styles.railCard,
                            ...(claim.id === selectedClaimID
                                ? styles.railCardSelected
                                : {}),
                        }}
                        onClick={() => setSelectedClaimID(claim.id)}
                    >
                        <div>{claim.facility_name}</div>
                        <div style={styles.railCardMeta}>
                            #{claim.id} · {claim.facility_country_name} ·{' '}
                            {ageInDays(claim.created_at)}d old
                        </div>
                    </button>
                ))}
            </nav>
            <main style={styles.workspace}>
                <ClaimWorkspace claimID={selectedClaimID} />
            </main>
        </div>
    );
}
