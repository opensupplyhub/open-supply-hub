export default function getSourcesCount(drawerData) {
    if (!drawerData) return 0;
    return Array.isArray(drawerData.contributions)
        ? drawerData.contributions.length
        : 0;
}
