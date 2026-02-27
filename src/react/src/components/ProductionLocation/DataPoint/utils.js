/**
 * Format a date string or Date for display (e.g. "Nov 2022").
 * @param {string|Date} date - ISO date string or Date
 * @returns {string} Formatted date
 */
export function formatDataPointDate(date) {
    if (!date) return '';
    const d = typeof date === 'string' ? new Date(date) : date;
    if (Number.isNaN(d.getTime())) return '';
    return d.toLocaleDateString('en-GB', {
        month: 'short',
        year: 'numeric',
    });
}

/**
 * Get the number of sources to display for the drawer trigger.
 * @param {object} drawerData - Data passed for the drawer
 * @returns {number} Count of sources (promoted + contributions)
 */
export function getSourcesCount(drawerData) {
    if (!drawerData) return 0;
    const promoted = drawerData.promotedContribution ? 1 : 0;
    const list = Array.isArray(drawerData.contributions)
        ? drawerData.contributions.length
        : 0;
    return promoted + list;
}
