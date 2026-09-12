import querystring, { stringify, parse } from '../../util/qs';

describe('qs.stringify', () => {
    it('serializes a flat object of strings', () => {
        expect(stringify({ a: '1', b: '2' })).toBe('a=1&b=2');
    });

    it('coerces numbers and booleans to strings', () => {
        expect(stringify({ n: 42, b: true })).toBe('n=42&b=true');
    });

    it('serializes arrays as repeated keys', () => {
        expect(stringify({ a: ['1', '2'] })).toBe('a=1&a=2');
    });

    it('emits an empty value for null and undefined (node parity)', () => {
        expect(stringify({ a: null, b: undefined })).toBe('a=&b=');
    });

    it('emits empty values for nullish array items rather than "null"/"undefined"', () => {
        expect(stringify({ a: [1, null, undefined, 2] })).toBe(
            'a=1&a=&a=&a=2',
        );
    });

    it('coerces non-primitive values to an empty string', () => {
        expect(stringify({ a: { nested: true } })).toBe('a=');
    });

    it('omits keys for empty arrays', () => {
        expect(stringify({ a: [], b: '1' })).toBe('b=1');
    });

    it('url-encodes reserved characters in keys and values', () => {
        expect(stringify({ 'a b': 'c&d' })).toBe('a+b=c%26d');
    });

    it('returns an empty string for null/undefined/empty input', () => {
        expect(stringify(null)).toBe('');
        expect(stringify(undefined)).toBe('');
        expect(stringify({})).toBe('');
    });
});

describe('qs.parse', () => {
    it('parses a flat query string into string values', () => {
        expect(parse('a=1&b=2')).toEqual({ a: '1', b: '2' });
    });

    it('collects repeated keys into an array', () => {
        expect(parse('a=1&a=2&a=3')).toEqual({ a: ['1', '2', '3'] });
    });

    it('keeps single occurrences as strings, not arrays', () => {
        const result = parse('a=1');
        expect(result.a).toBe('1');
        expect(Array.isArray(result.a)).toBe(false);
    });

    it('tolerates a leading question mark', () => {
        expect(parse('?a=1&b=2')).toEqual({ a: '1', b: '2' });
    });

    it('decodes percent- and plus-encoded values', () => {
        expect(parse('a+b=c%26d')).toEqual({ 'a b': 'c&d' });
    });

    it('represents keys with no value as empty strings', () => {
        expect(parse('a=&b=2')).toEqual({ a: '', b: '2' });
    });

    it('returns an empty object for an empty string', () => {
        expect(parse('')).toEqual({});
    });

    it('preserves "__proto__" as an own key without polluting the prototype (node parity)', () => {
        const result = parse('__proto__=x');

        expect(Object.hasOwn(result, '__proto__')).toBe(true);
        // Read via descriptor rather than result.__proto__ (no-proto rule).
        expect(Object.getOwnPropertyDescriptor(result, '__proto__').value).toBe(
            'x',
        );
        // The prototype itself must be untouched.
        expect({}.polluted).toBeUndefined();
        expect(Object.getPrototypeOf(result)).toBeNull();
    });

    it('collects repeated "__proto__" keys into an array', () => {
        const result = parse('__proto__=1&__proto__=2');

        expect(
            Object.getOwnPropertyDescriptor(result, '__proto__').value,
        ).toEqual(['1', '2']);
    });
});

describe('qs round-trip', () => {
    it('preserves a filter-shaped object through stringify -> parse', () => {
        const input = {
            countries: ['US', 'CN'],
            q: 'cotton mill',
            page: '2',
        };
        expect(parse(stringify(input))).toEqual(input);
    });
});

describe('qs default export', () => {
    it('exposes stringify and parse', () => {
        expect(querystring.stringify).toBe(stringify);
        expect(querystring.parse).toBe(parse);
    });
});
