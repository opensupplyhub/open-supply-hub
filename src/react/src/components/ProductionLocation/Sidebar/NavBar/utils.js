import env from '../../../../util/env';
import { HEADER_HEIGHT } from '../../../../util/constants';

/**
 * Smoothly scrolls the window to the top position
 * of the given element, offset by the header height.
 *
 * @param {HTMLElement} element - The DOM element to scroll to.
 */
export function scrollToSection(element) {
    if (!element) {
        return;
    }

    const top =
        element.getBoundingClientRect().top + window.scrollY - HEADER_HEIGHT;
    window.scrollTo({ top, behavior: 'smooth' });
}

/**
 * When Django saves the icon URL, it uses the "minio" hostname
 * because it is running within the same network and cannot use "localhost".
 * This function replaces the hostname with "localhost" for local development.
 *
 * @param {string} url - The original icon URL.
 * @returns {string} The processed icon URL.
 */
export function getIconURL(url) {
    const environment = env('ENVIRONMENT');

    if (environment === 'local') {
        return url.replace('minio', 'localhost');
    }

    return url;
}
