import env from '../../../../util/env';

/**
 * Returns the icon URL, replacing 'minio' with 'localhost'
 * if the environment is local. Otherwise, returns the original URL.
 *
 * @param {string} url - The original icon URL.
 * @returns {string} The processed icon URL.
 */
export default function getIconURL(url) {
    const environment = env('ENVIRONMENT');

    if (environment === 'local') {
        return url.replace('minio', 'localhost');
    }

    return url;
}
