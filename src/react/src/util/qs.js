/*
 * Drop-in replacement for node's `querystring` module, which webpack 4
 * polyfilled in the browser but Vite (correctly) externalizes.
 *
 * Reproduces the semantics the app relies on, built on URLSearchParams:
 * - stringify: arrays serialize as repeated keys ({a: [1, 2]} -> "a=1&a=2")
 * - parse: repeated keys collect into arrays ("a=1&a=2" -> {a: ['1', '2']}),
 *   single occurrences stay strings
 *
 * Encoding note: URLSearchParams encodes spaces as "+" where node used
 * "%20". Both decode identically here and in Django, so round-trips and
 * bookmarked URLs keep working.
 */
// Match node's querystring.stringify coercion: strings/numbers/booleans
// serialize as-is; null, undefined, and any non-primitive become "".
// The key is always emitted (e.g. {a: null} -> "a="), including for each
// array item, so nothing leaks as the literal "null"/"undefined" strings
// that URLSearchParams would otherwise produce.
const toPrimitive = v => {
    const t = typeof v;
    if (t === 'string') return v;
    if (t === 'number' || t === 'boolean' || t === 'bigint') return String(v);
    return '';
};

export const stringify = obj => {
    const params = new URLSearchParams();

    Object.keys(obj || {}).forEach(key => {
        const value = obj[key];

        if (Array.isArray(value)) {
            value.forEach(v => params.append(key, toPrimitive(v)));
        } else {
            params.append(key, toPrimitive(value));
        }
    });

    return params.toString();
};

export const parse = qs => {
    const params = new URLSearchParams(qs);
    // Object.create(null) matches node's querystring.parse (which returns a
    // null-prototype object). This preserves keys like "__proto__" as own
    // properties instead of hitting Object.prototype's setter and dropping
    // them, and avoids any prototype-pollution surface.
    const result = Object.create(null);

    params.forEach((value, key) => {
        if (Object.hasOwn(result, key)) {
            if (Array.isArray(result[key])) {
                result[key].push(value);
            } else {
                result[key] = [result[key], value];
            }
        } else {
            result[key] = value;
        }
    });

    return result;
};

export default { stringify, parse };
