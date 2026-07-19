/*
 * Dependency-free replacement for `object-hash`, which was abandoned in
 * 2019 and whose browser bundle cannot run under strict-mode ESM (Vite).
 *
 * Produces a deterministic 8-character hex digest of any JSON-like value.
 * Object keys are sorted recursively, so logically equal filter objects
 * hash identically regardless of key insertion order (matching the
 * unorderedObjects behavior of object-hash that tile cache keys relied
 * on). This is a cache key, not a security primitive — a 32-bit FNV-1a
 * digest is sufficient and needs no crypto.
 */
const stableStringify = value => {
    if (value === null || typeof value !== 'object') {
        return JSON.stringify(value);
    }

    if (Array.isArray(value)) {
        return `[${value.map(stableStringify).join(',')}]`;
    }

    const keys = Object.keys(value).sort();
    const entries = keys.map(
        k => `${JSON.stringify(k)}:${stableStringify(value[k])}`,
    );
    return `{${entries.join(',')}}`;
};

export default function stableHash(value) {
    const str = stableStringify(value);

    /* eslint-disable no-bitwise */
    let h = 0x811c9dc5; // FNV-1a offset basis
    for (let i = 0; i < str.length; i += 1) {
        h ^= str.charCodeAt(i);
        h = Math.imul(h, 0x01000193); // FNV prime
    }
    return (h >>> 0).toString(16).padStart(8, '0');
    /* eslint-enable no-bitwise */
}
