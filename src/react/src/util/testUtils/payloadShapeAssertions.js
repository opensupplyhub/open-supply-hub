/*
 * Helpers for pinning the payload a form surface hands to the API layer.
 *
 * The forms keep select choices as { value, label } option objects, and
 * every submit path must unwrap them before the request goes out. Two
 * surfaces that did not (OSDEV-3737, OSDEV-3740) shipped payloads the
 * API rejected, so payload tests use these to sweep a whole request body
 * for leaked option objects rather than checking fields one by one.
 */

/**
 * Paths (e.g. 'isic_4[0]') of every object carrying both `value` and
 * `label` keys anywhere in a JSON-serializable payload. An empty result
 * means no react-select option object leaked into the request body.
 */
export const findSelectOptionObjects = (payload, path = '') => {
    if (Array.isArray(payload)) {
        return payload.reduce(
            (found, item, index) =>
                found.concat(
                    findSelectOptionObjects(item, `${path}[${index}]`),
                ),
            [],
        );
    }
    if (payload !== null && typeof payload === 'object') {
        if ('value' in payload && 'label' in payload) {
            return [path || '(root)'];
        }
        return Object.entries(payload).reduce(
            (found, [key, item]) =>
                found.concat(
                    findSelectOptionObjects(
                        item,
                        path ? `${path}.${key}` : key,
                    ),
                ),
            [],
        );
    }
    return [];
};

/**
 * Every entry of a FormData payload, keyed by field name, so a multipart
 * body can be asserted exactly.
 */
export const formDataEntries = postData => {
    const entries = {};
    [...postData.keys()].forEach(key => {
        entries[key] = postData.getAll(key);
    });
    return entries;
};

/**
 * Field names of FormData entries that coerced an object to the
 * '[object Object]' string — what the API receives when an option object
 * is appended to a multipart payload unconverted.
 */
export const findObjectCoercions = postData =>
    [...postData.entries()]
        .filter(([, value]) => String(value).includes('[object Object]'))
        .map(([key]) => key);
