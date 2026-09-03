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
 * Count Mon-Fri days strictly after `start` up to and including `end`.
 * Same naive walk (no holiday calendar) as the pipeline's
 * add_business_days, so the dashboard and the reminder/denial queues
 * agree on what "15 business days" means.
 */
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
    const cursor = new Date(startDate);
    cursor.setHours(0, 0, 0, 0);
    const endDay = new Date(endDate);
    endDay.setHours(0, 0, 0, 0);
    while (cursor < endDay) {
        cursor.setDate(cursor.getDate() + 1);
        const weekday = cursor.getDay();
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
        n => n && n.note_type === NOTE_TYPES.CLAIMANT_MESSAGE,
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

    // A claimant update after the last outbound message means there is
    // new information to review — the claim is no longer "awaiting".
    // (CLAIMANT_UPDATE notes are written by the OSDEV-2278 claimant-edit
    // flow; a dedicated "claimant updated" stage is deferred, so these
    // claims surface at the top of "new".)
    const updatesSinceMessage = safeNotes.filter(
        n =>
            n &&
            n.note_type === NOTE_TYPES.CLAIMANT_UPDATE &&
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
