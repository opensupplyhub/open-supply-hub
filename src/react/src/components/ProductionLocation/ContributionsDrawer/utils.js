/**
 * Format a date for display in the drawer (e.g. "Nov 2022").
 * @param {string|Date} date - ISO date string or Date
 * @returns {string}
 */
export default function formatContributionDate(date) {
    if (!date) return '';
    const d = typeof date === 'string' ? new Date(date) : date;
    if (Number.isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-GB', {
        month: 'short',
        year: 'numeric',
    });
}
