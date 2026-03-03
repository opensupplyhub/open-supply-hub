/**
 * Format a date string or Date for display in Production Location UI
 * (e.g. "November 12, 2022").
 * @param {string|Date} date - ISO date string or Date
 * @returns {string} Formatted date
 */
export function formatDisplayDate(date) {
    if (!date) return '';
    const d = typeof date === 'string' ? new Date(date) : date;
    if (Number.isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-US', {
        month: 'long',
        day: 'numeric',
        year: 'numeric',
    });
}
