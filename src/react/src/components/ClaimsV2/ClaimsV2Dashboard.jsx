import React, { useEffect, useMemo, useRef, useState } from 'react';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';

import { useClaimsList, useClaimDetail, useClaimActions } from './hooks';
import { parseAutomatedReview, P1_MARKER } from './automatedReviewUtils';
import DecisionPanel from './DecisionPanel';
import EvidencePanel from './EvidencePanel';
import InternalNoteBox from './InternalNoteBox';
import MessageComposer from './MessageComposer';
import VerificationPanel from './VerificationPanel';
import { deriveClaimStage, CLAIM_STAGES, NOTE_TYPES } from './stageUtils';
import {
    buildQueueGroups,
    nextVisibleClaimID,
    regionOptions,
    claimAgeDays,
    ALL_REGIONS,
    SORT_ORDERS,
} from './railUtils';

const formatDate = value => {
    const date = new Date(value);
    return Number.isNaN(date.getTime())
        ? String(value)
        : date.toLocaleDateString(undefined, {
              year: 'numeric',
              month: 'short',
              day: 'numeric',
          });
};
import QueueRail from './QueueRail';
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

function ClaimWorkspace({ claimID, onDecided }) {
    const { detail, fetching, error, refetchDetail } = useClaimDetail(claimID);
    const {
        acting,
        actionError,
        messageClaimant,
        approveClaim,
        denyClaim,
        addNote,
    } = useClaimActions(claimID);

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
    const review = parseAutomatedReview(detail.notes);
    const facilityName =
        detail.facility?.properties?.name || `Claim #${detail.id}`;
    const statusChange = detail.status_change || {};
    // The API orders notes by insertion id; sort by created_at so
    // backdated or imported notes still read chronologically.
    const timelineNotes = [...(detail.notes || [])].sort(
        (a, b) => new Date(a.created_at) - new Date(b.created_at),
    );

    return (
        <div>
            <Typography variant="title" gutterBottom>
                {facilityName}{' '}
                <span style={styles.noteMeta}>Claim #{detail.id}</span>
            </Typography>
            <p style={styles.workspaceSub}>
                Submitted <strong>{formatDate(detail.created_at)}</strong> (
                {claimAgeDays(detail.created_at)} days ago) by{' '}
                <strong>{detail.contact_person}</strong>
                {detail.job_title ? `, ${detail.job_title}` : ''} ·{' '}
                <strong>{detail.email}</strong>
            </p>
            <p style={styles.workspaceSub}>
                Organization: <strong>{detail.company_name || '—'}</strong>
                {detail.facility?.properties?.country_name
                    ? ` · ${detail.facility.properties.country_name}`
                    : ''}
            </p>
            {/* Top grid (§5b): profile/status main column beside the
                ~38% Decision rail. The verification panel joins the
                main column in a later increment. */}
            <div style={styles.topGrid}>
                <div style={styles.topGridMain}>
                    <div style={styles.stageBox}>
                        <strong>{STAGE_LABELS[stage.stage]}</strong>
                    </div>
                    {/* Profile anchor (§4/§5b): what the claimant is
                        claiming, with the jump to the live profile. */}
                    <div style={styles.profileAnchor}>
                        <div style={styles.sectionLabel}>
                            OS Hub profile — what the claimant is claiming
                        </div>
                        <div style={styles.profileName}>
                            {detail.facility?.properties?.name || '—'}
                        </div>
                        <div style={styles.profileAddress}>
                            {detail.facility?.properties?.address || ''}
                        </div>
                        {detail.facility?.id && (
                            <div style={styles.profileOsId}>
                                <a
                                    href={`/facilities/${detail.facility.id}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    {detail.facility.id} — open profile ↗
                                </a>
                            </div>
                        )}
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
                    <VerificationPanel detail={detail} review={review} />
                </div>
                {detail.status === 'PENDING' && (
                    <DecisionPanel
                        detail={detail}
                        stage={stage}
                        acting={acting}
                        approveClaim={approveClaim}
                        denyClaim={denyClaim}
                        addNote={addNote}
                        onDecided={() => {
                            refetchDetail();
                            onDecided();
                        }}
                    />
                )}
            </div>
            {/* Workbench (§5b): evidence beside the composer, so the
                extracted/translated text sits next to the draft. Keyed
                by claim so the first document auto-opens on J/K moves. */}
            <div style={styles.workbench} key={detail.id}>
                <EvidencePanel
                    attachments={detail.attachments}
                    review={review}
                    matchValues={[
                        ['Name', detail.facility?.properties?.name],
                        ['Address', detail.facility?.properties?.address],
                        [
                            'Person & title',
                            [detail.contact_person, detail.job_title]
                                .filter(Boolean)
                                .join(' — '),
                        ],
                        ['Email', detail.email],
                    ]}
                />
                <MessageComposer
                    detail={detail}
                    review={review}
                    messageClaimant={messageClaimant}
                    acting={acting}
                    onSent={refetchDetail}
                />
            </div>
            {actionError && (
                <Typography variant="body1" style={styles.evidenceHint}>
                    {actionError}
                </Typography>
            )}
            <div>
                <div style={styles.sectionLabel}>Activity</div>
                <InternalNoteBox
                    addNote={addNote}
                    acting={acting}
                    onAdded={refetchDetail}
                />
                {timelineNotes.map(note => (
                    <div key={note.id} style={styles.noteItem}>
                        <div style={styles.noteMeta}>
                            {note.author} · {note.created_at}
                            <span style={styles.noteTag}>
                                {NOTE_TAG_LABELS[note.note_type] ||
                                    // Show an unknown type raw rather than
                                    // mislabeling its direction; only a
                                    // missing type means legacy-internal.
                                    note.note_type ||
                                    NOTE_TAG_LABELS[NOTE_TYPES.INTERNAL]}
                            </span>
                        </div>
                        <div>
                            {/* The pipeline's machine-readable block is
                                parsed into the workbench, not read as
                                prose — show only the human part here. */}
                            {note.note?.includes(P1_MARKER) ? (
                                <>
                                    {note.note
                                        .slice(0, note.note.indexOf(P1_MARKER))
                                        .trim()}
                                    <div style={styles.evidenceHint}>
                                        🤖 Automated review data attached (shown
                                        in the evidence viewer and suggested
                                        draft).
                                    </div>
                                </>
                            ) : (
                                note.note
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

const isTypingTarget = target =>
    target &&
    (target.tagName === 'INPUT' ||
        target.tagName === 'TEXTAREA' ||
        target.tagName === 'SELECT' ||
        target.isContentEditable);

export default function ClaimsV2Dashboard() {
    const { claims, fetching, error, refetchClaims } = useClaimsList();
    const [selectedClaimID, setSelectedClaimID] = useState(null);
    const [query, setQuery] = useState('');
    const [region, setRegion] = useState(ALL_REGIONS);
    const [sort, setSort] = useState(SORT_ORDERS.OLDEST);
    const [railCollapsed, setRailCollapsed] = useState(false);
    const searchInputRef = useRef(null);

    const { groups, visibleIds } = useMemo(
        () => buildQueueGroups(claims, { query, region, sort }),
        [claims, query, region, sort],
    );
    const regions = useMemo(() => regionOptions(claims), [claims]);

    /*
     * Auto-select the first visible claim on load, and move the
     * selection back into view when a filter change hides it —
     * the workspace should never show a claim absent from the rail.
     */
    useEffect(() => {
        if (visibleIds.length === 0) {
            setSelectedClaimID(null);
        } else if (!visibleIds.includes(selectedClaimID)) {
            setSelectedClaimID(visibleIds[0]);
        }
    }, [visibleIds, selectedClaimID]);

    /*
     * Global keys (spec §4): J/K and ↓/↑ walk the rail in on-screen
     * order; `/` focuses search. All are inert while typing in a
     * field, so the composer and search box keep their letters.
     */
    useEffect(() => {
        const onKeyDown = event => {
            if (
                event.metaKey ||
                event.ctrlKey ||
                event.altKey ||
                isTypingTarget(event.target)
            ) {
                return;
            }
            const key = event.key.toLowerCase();
            if (key === '/') {
                event.preventDefault();
                if (searchInputRef.current) searchInputRef.current.focus();
                return;
            }
            let delta = 0;
            if (key === 'j' || event.key === 'ArrowDown') {
                delta = 1;
            } else if (key === 'k' || event.key === 'ArrowUp') {
                delta = -1;
            }
            if (delta !== 0) {
                event.preventDefault();
                setSelectedClaimID(current =>
                    nextVisibleClaimID(visibleIds, current, delta),
                );
            }
        };
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [visibleIds]);

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
            <QueueRail
                groups={groups}
                visibleCount={visibleIds.length}
                selectedClaimID={selectedClaimID}
                onSelect={setSelectedClaimID}
                query={query}
                onQueryChange={setQuery}
                region={region}
                onRegionChange={setRegion}
                regions={regions}
                sort={sort}
                onToggleSort={() =>
                    setSort(current =>
                        current === SORT_ORDERS.OLDEST
                            ? SORT_ORDERS.NEWEST
                            : SORT_ORDERS.OLDEST,
                    )
                }
                searchInputRef={searchInputRef}
                railCollapsed={railCollapsed}
                onToggleRail={() => setRailCollapsed(current => !current)}
            />
            <main style={styles.workspace}>
                <ClaimWorkspace
                    claimID={selectedClaimID}
                    onDecided={refetchClaims}
                />
            </main>
        </div>
    );
}
