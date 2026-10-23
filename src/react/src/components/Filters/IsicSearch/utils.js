// Entries come from GET /api/taxonomy/isic/: one per level and title, with
// the code it has in each ISIC revision ({ id, title, level, codes, trail }).

export const REVISION_LABELS = Object.freeze({ 4: 'ISIC 4', 5: 'ISIC 5' });
export const LEVEL_LABELS = Object.freeze({
    section: 'Section',
    division: 'Division',
    group: 'Group',
    class: 'Class',
});
const LEVEL_ORDER = Object.freeze(['section', 'division', 'group', 'class']);
const MAX_RESULTS = 25;

export const normalize = text =>
    text
        .toLowerCase()
        .replace(/[^a-z0-9& ]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();

// Exact title, then titles starting with the query, then titles with a word
// starting with each query word, then titles containing it.
const scoreTitle = (title, query) => {
    const text = normalize(title);
    if (text === query) return 1000;
    if (text.startsWith(query)) return 900;
    const words = text.split(' ');
    const queryWords = query.split(' ');
    if (queryWords.every(q => words.some(word => word.startsWith(q)))) {
        return 800 - words.findIndex(word => word.startsWith(queryWords[0]));
    }
    return text.includes(query) ? 500 : -1;
};

export function searchEntries(entries, query, selectedIds) {
    const normalized = normalize(query);
    if (!normalized) return [];

    return entries
        .map(entry => ({ entry, score: scoreTitle(entry.title, normalized) }))
        .filter(({ entry, score }) => score >= 0 && !selectedIds.has(entry.id))
        .sort(
            (a, b) =>
                b.score - a.score ||
                LEVEL_ORDER.indexOf(a.entry.level) -
                    LEVEL_ORDER.indexOf(b.entry.level) ||
                a.entry.title.localeCompare(b.entry.title),
        )
        .slice(0, MAX_RESULTS)
        .map(({ entry }) => entry);
}

// The isic_4 / isic_5 filter value of an entry in one revision.
export const filterValue = (entry, revision) =>
    `${entry.level}:${entry.codes[revision]}`;

export const revisionsOf = entry => Object.keys(entry.codes).sort();

// The selected entries, read back from the isic4 / isic5 filters.
export function selectedEntries(entries, selections) {
    const byValue = new Map();
    entries.forEach(entry =>
        revisionsOf(entry).forEach(revision =>
            byValue.set(`${revision}|${filterValue(entry, revision)}`, entry),
        ),
    );

    const selected = new Map();
    Object.entries(selections).forEach(([revision, options]) =>
        options.forEach(({ value }) => {
            const entry = byValue.get(`${revision}|${value}`);
            if (entry) selected.set(entry.id, entry);
        }),
    );
    return [...selected.values()];
}

// The isic4 / isic5 filters with an entry added or removed.
export function withEntry(selections, entry, include) {
    const next = {};
    Object.entries(selections).forEach(([revision, options]) => {
        const value = entry.codes[revision] && filterValue(entry, revision);
        const kept = options.filter(option => option.value !== value);
        next[revision] =
            include && value ? [...kept, { value, label: entry.title }] : kept;
    });
    return next;
}
