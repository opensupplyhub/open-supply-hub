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
        if (parsed && parsed.v === 1 && parsed.kind === 'automated_review') {
            return parsed;
        }
    } catch (e) {
        // Malformed block: treat as absent rather than erroring the UI.
    }
    return null;
};

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

/*
 * Extracted/translated text for one attachment, or null when the
 * pipeline has none for it (cached-translation gap, non-document
 * files, or no automation at all — SPEC.md §P1 known data gap).
 */
export const getEvidenceText = (review, fileName) => {
    const entry = review?.evidence?.[fileName];
    if (!entry || (!entry.original && !entry.translated)) {
        return null;
    }
    return {
        original: entry.original || null,
        translated: entry.translated || null,
        lang: entry.lang || null,
    };
};

export const getSuggestedDraft = review =>
    typeof review?.draft === 'string' && review.draft.trim() !== ''
        ? review.draft
        : null;

export const isPdfFile = fileName =>
    typeof fileName === 'string' && /\.pdf$/i.test(fileName.trim());
