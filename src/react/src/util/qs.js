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
export const stringify = obj => {
    const params = new URLSearchParams();

    Object.keys(obj || {}).forEach(key => {
        const value = obj[key];

        if (value === undefined) {
            return;
        }

        if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
        } else {
            params.append(key, value);
        }
    });

    return params.toString();
};

export const parse = qs => {
    const params = new URLSearchParams(qs);
    const result = {};

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
