/*
 * Parser for the automated-review machine-readable note block (SPEC.md
 * §P1) — the single data contract between the claims pipeline and the
 * v2 frontend. A pipeline note carries a fenced JSON payload after the
 * marker line; it feeds the evidence viewer's original/translation tabs
 * and the ★ suggested draft here (OSDEV-3356 workbench), and the
 * verification-panel scores in a later increment.
 *
 * Everything degrades to null when the block is absent, unparseable,
 * or a version we don't understand — the UI must work without it.
 */

export const P1_MARKER = '--- machine-readable, do not edit ---';

const parseBlock = text => {
    if (typeof text !== 'string') {
        return null;
    }
    const markerIndex = text.indexOf(P1_MARKER);
    if (markerIndex === -1) {
        return null;
    }
    const jsonStart = text.indexOf('{', markerIndex);
    if (jsonStart === -1) {
        return null;
    }
    try {
        const parsed = JSON.parse(text.slice(jsonStart));
        if (parsed?.v === 1 && parsed?.kind === 'automated_review') {
            return parsed;
        }
    } catch (e) {
        // Malformed block: treat as absent rather than erroring the UI.
    }
    return null;
};

/*
 * Whether a note's machine-readable block parses as a version we
 * understand — the timeline compacts a note only when it does;
 * otherwise the raw note stays visible so unparseable automation
 * output is never unreachable.
 */
export const hasValidReviewBlock = text => parseBlock(text) !== null;

/*
 * Find the automated review for a claim from its notes. The newest
 * valid block wins — the pipeline may re-run on a claim.
 */
export const parseAutomatedReview = notes => {
    const candidates = (Array.isArray(notes) ? notes : [])
        .map(note => ({
            review: parseBlock(note?.note),
            createdAt: new Date(note?.created_at),
        }))
        .filter(entry => entry.review !== null)
        .sort((a, b) => b.createdAt - a.createdAt);
    return candidates.length > 0 ? candidates[0].review : null;
};

/* Filename without its final extension ("badge.pdf" → "badge"). */
const stemOf = name => String(name).replace(/\.[^./\\]+$/, '');

/*
 * Does an evidence key belong to this attachment? Exact match, or the
 * legacy artifact name: blocks posted before the pipeline carried the
 * original file name keyed text by Path(...).with_suffix('.json'), so
 * "badge.pdf" sits under "badge.json". Only that ".json" shape may
 * stand in — any other same-stem key ("license.jpg" next to
 * "license.pdf") is a different document and must never be shown as
 * this one's text. URL evidence is keyed by the exact URL and never
 * stem-matched: ".../license.pdf" and ".../license.json" are different
 * pages, and legacy artifact names are bare filenames, so nothing
 * containing "://" is ever a legacy key.
 */
export const matchesEvidenceKey = (fileName, key) =>
    key === fileName ||
    (!String(fileName).includes('://') &&
        !String(key).includes('://') &&
        /\.json$/i.test(String(key)) &&
        stemOf(key) === stemOf(fileName));

/*
 * Extracted/translated text for one attachment, or null when the
 * pipeline has none for it (cached-translation gap, non-document
 * files, or no automation at all — SPEC.md §P1 known data gap).
 *
 * Lookup is exact-first with a legacy-key fallback (see
 * matchesEvidenceKey), which recovers the text for every note posted
 * before the pipeline keyed evidence by the original file name.
 */
export const getEvidenceText = (review, fileName) => {
    const evidence = review?.evidence;
    if (!evidence || !fileName) {
        return null;
    }
    let entry = evidence[fileName];
    if (!entry) {
        const legacyKey = Object.keys(evidence).find(key =>
            matchesEvidenceKey(fileName, key),
        );
        entry = legacyKey ? evidence[legacyKey] : undefined;
    }
    if (!entry || (!entry.original && !entry.translated)) {
        return null;
    }
    return {
        original: entry.original || null,
        translated: entry.translated || null,
        lang: entry.lang || null,
    };
};

/*
 * Per-criterion value extracted from the documents (the P2 tier-2
 * extension of the block: optional "extracts" — {key: {value, source}}
 * where source is the attachment file name it was found in). Returns
 * null until the pipeline ships it; the verification rows degrade to
 * reasoning-only.
 */
export const getExtract = (review, key) => {
    const entry = review?.extracts?.[key];
    if (!entry || typeof entry.value !== 'string' || entry.value === '') {
        return null;
    }
    return {
        value: entry.value,
        source: typeof entry.source === 'string' ? entry.source : null,
    };
};

export const getSuggestedDraft = review =>
    typeof review?.draft === 'string' && review.draft.trim() !== ''
        ? review.draft
        : null;

export const isPdfFile = fileName =>
    typeof fileName === 'string' && /\.pdf$/i.test(fileName.trim());
