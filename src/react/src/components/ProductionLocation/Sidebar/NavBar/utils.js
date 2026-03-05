import env from '../../../../util/env';

/**
 * When Django saves the icon URL, it uses the "minio" hostname
 * because it is running within the same network and cannot use "localhost".
 * This function replaces the hostname with "localhost" for local development.
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
