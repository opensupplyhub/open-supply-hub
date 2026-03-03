/**
 * Get the number of sources to display for the drawer trigger.
 * @param {object} drawerData - Data passed for the drawer
 * @returns {number} Count of sources (promoted + contributions)
 */
export function getSourcesCount(drawerData) {
    if (!drawerData) return 0;
    return Array.isArray(drawerData.contributions)
        ? drawerData.contributions.length
        : 0;
}
