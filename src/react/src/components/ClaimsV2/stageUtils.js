/*
 * Queue-stage derivation for claims dashboard v2 (OSDEV-3355).
 *
 * Stages are derived from the claim's review-note timeline using the
 * note_type field added in OSDEV-3351:
 *
 *   new      — no CLAIMANT_MESSAGE has been sent (or the claimant has
 *              acted since the last one and the claim needs review)
 *   awaiting — messaged, no claimant activity since, within the window
 *   overdue  — messaged more than REPLY_OVERDUE_BUSINESS_DAYS business
 *              days ago with no claimant activity since
 *
 * Pre-OSDEV-3351 notes have note_type INTERNAL (the migration default),
 * so legacy claims degrade to "new" until fresh messages are sent —
 * the documented cutoff behavior, not an error.
 */

export const CLAIM_STAGES = Object.freeze({
    NEW: 'new',
    AWAITING: 'awaiting',
    OVERDUE: 'overdue',
});

export const NOTE_TYPES = Object.freeze({
    INTERNAL: 'INTERNAL',
    CLAIMANT_MESSAGE: 'CLAIMANT_MESSAGE',
    CLAIMANT_UPDATE: 'CLAIMANT_UPDATE',
});

// Mirrors the automated-claims reminder/denial window: the claimant is
// promised a reply window of 15 business days.
export const REPLY_OVERDUE_BUSINESS_DAYS = 15;

/*
 * Count Mon-Fri days strictly after `start` up to and including `end`,
 * on UTC calendar dates. UTC (not the viewer's local timezone) so
 * every moderator sees the same stage and the count matches the
 * pipeline's add_business_days, which walks UTC dates — the same
 * naive walk, no holiday calendar.
 */
const DAY_MS = 24 * 60 * 60 * 1000;

export const businessDaysBetween = (start, end) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (
        Number.isNaN(startDate.getTime()) ||
        Number.isNaN(endDate.getTime()) ||
        endDate <= startDate
    ) {
        return 0;
    }
    let count = 0;
    let cursor = Date.UTC(
        startDate.getUTCFullYear(),
        startDate.getUTCMonth(),
        startDate.getUTCDate(),
    );
    const endDay = Date.UTC(
        endDate.getUTCFullYear(),
        endDate.getUTCMonth(),
        endDate.getUTCDate(),
    );
    while (cursor < endDay) {
        cursor += DAY_MS;
        const weekday = new Date(cursor).getUTCDay();
        if (weekday !== 0 && weekday !== 6) {
            count += 1;
        }
    }
    return count;
};

const latestOf = notes =>
    notes.reduce(
        (latest, note) =>
            !latest || new Date(note.created_at) > new Date(latest.created_at)
                ? note
                : latest,
        null,
    );

/*
 * Derive the queue stage for one claim from its notes array (the claim
 * detail response's `notes`, each carrying note_type per OSDEV-3351).
 *
 * Returns { stage, reason, lastMessagedAt, waitingBusinessDays }.
 * `reason` is the human-readable "why it's in this stage" line shown in
 * the workspace decision panel.
 */
export const deriveClaimStage = (notes, { now = new Date() } = {}) => {
    const safeNotes = Array.isArray(notes) ? notes : [];
    const messages = safeNotes.filter(
        n => n?.note_type === NOTE_TYPES.CLAIMANT_MESSAGE,
    );

    if (messages.length === 0) {
        return {
            stage: CLAIM_STAGES.NEW,
            reason:
                'No moderator message yet — derived from an empty ' +
                'outbound timeline.',
            lastMessagedAt: null,
            waitingBusinessDays: 0,
        };
    }

    const lastMessage = latestOf(messages);
    const lastMessagedAt = lastMessage.created_at;

    // A message whose timestamp cannot be read must escalate, not sit
    // in "awaiting" forever with a clock that never advances.
    if (Number.isNaN(new Date(lastMessagedAt).getTime())) {
        return {
            stage: CLAIM_STAGES.NEW,
            reason:
                'The last message has an unreadable timestamp — the ' +
                'reply window cannot be tracked, review manually.',
            lastMessagedAt,
            waitingBusinessDays: 0,
        };
    }

    // A claimant update after the last outbound message means there is
    // new information to review — the claim is no longer "awaiting".
    // (CLAIMANT_UPDATE notes are written by the OSDEV-2278 claimant-edit
    // flow; a dedicated "claimant updated" stage is deferred, so these
    // claims surface at the top of "new".)
    const updatesSinceMessage = safeNotes.filter(
        n =>
            n?.note_type === NOTE_TYPES.CLAIMANT_UPDATE &&
            new Date(n.created_at) > new Date(lastMessagedAt),
    );
    if (updatesSinceMessage.length > 0) {
        return {
            stage: CLAIM_STAGES.NEW,
            reason:
                'The claimant updated this claim after the last message ' +
                '— review the new information.',
            lastMessagedAt,
            waitingBusinessDays: 0,
        };
    }

    const waitingBusinessDays = businessDaysBetween(lastMessagedAt, now);
    if (waitingBusinessDays > REPLY_OVERDUE_BUSINESS_DAYS) {
        return {
            stage: CLAIM_STAGES.OVERDUE,
            reason:
                `No reply for ${waitingBusinessDays} business days — past ` +
                `the ${REPLY_OVERDUE_BUSINESS_DAYS}-business-day window ` +
                'promised to the claimant.',
            lastMessagedAt,
            waitingBusinessDays,
        };
    }

    return {
        stage: CLAIM_STAGES.AWAITING,
        reason:
            `Messaged ${waitingBusinessDays} business day(s) ago, no ` +
            'claimant activity since — within the ' +
            `${REPLY_OVERDUE_BUSINESS_DAYS}-business-day window.`,
        lastMessagedAt,
        waitingBusinessDays,
    };
};
