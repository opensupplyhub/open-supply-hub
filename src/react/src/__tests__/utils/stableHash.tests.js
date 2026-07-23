import stableHash from '../../util/stableHash';

describe('stableHash', () => {
    it('returns an 8-character lowercase hex digest', () => {
        expect(stableHash({ a: 1 })).toMatch(/^[0-9a-f]{8}$/);
    });

    it('is deterministic for the same input', () => {
        const value = { countries: ['US', 'CN'], q: 'cotton' };
        expect(stableHash(value)).toBe(stableHash(value));
    });

    it('is insensitive to key insertion order', () => {
        expect(stableHash({ a: 1, b: 2 })).toBe(stableHash({ b: 2, a: 1 }));
    });

    it('sorts keys recursively (nested objects)', () => {
        const a = { outer: { x: 1, y: 2 }, z: 3 };
        const b = { z: 3, outer: { y: 2, x: 1 } };
        expect(stableHash(a)).toBe(stableHash(b));
    });

    it('is sensitive to values', () => {
        expect(stableHash({ a: 1 })).not.toBe(stableHash({ a: 2 }));
    });

    it('is sensitive to keys', () => {
        expect(stableHash({ a: 1 })).not.toBe(stableHash({ b: 1 }));
    });

    it('preserves array order (arrays are not sorted)', () => {
        expect(stableHash({ a: [1, 2] })).not.toBe(stableHash({ a: [2, 1] }));
    });

    it('distinguishes types that share a string form', () => {
        expect(stableHash({ a: 1 })).not.toBe(stableHash({ a: '1' }));
        expect(stableHash({ a: null })).not.toBe(
            stableHash({ a: 'null' }),
        );
    });

    it('distinguishes an empty object from an empty array', () => {
        expect(stableHash({})).not.toBe(stableHash([]));
    });

    it('handles primitives and nullish input without throwing', () => {
        expect(stableHash('x')).toMatch(/^[0-9a-f]{8}$/);
        expect(stableHash(0)).toMatch(/^[0-9a-f]{8}$/);
        expect(stableHash(null)).toMatch(/^[0-9a-f]{8}$/);
        expect(stableHash(undefined)).toMatch(/^[0-9a-f]{8}$/);
    });

    it('distinguishes null from undefined, at top level and nested', () => {
        expect(stableHash(null)).not.toBe(stableHash(undefined));
        expect(stableHash({ a: null })).not.toBe(
            stableHash({ a: undefined }),
        );
    });

    it('treats a nested undefined consistently with a top-level undefined token', () => {
        // Regression guard: nested undefined must not throw or coerce to the
        // literal string "undefined".
        expect(stableHash({ a: undefined })).toMatch(/^[0-9a-f]{8}$/);
        expect(stableHash({ a: undefined })).not.toBe(
            stableHash({ a: 'undefined' }),
        );
    });

    it('does not collide on a small set of similar filter objects', () => {
        const inputs = [
            {},
            { countries: ['US'] },
            { countries: ['CN'] },
            { countries: ['US', 'CN'] },
            { countries: ['US'], q: 'a' },
            { q: 'a' },
        ];
        const hashes = inputs.map(stableHash);
        expect(new Set(hashes).size).toBe(inputs.length);
    });
});
