import { CONTRIBUTIONS_SECTION_LABEL } from './constants';

export const getContributionsCount = contributions =>
    Array.isArray(contributions) ? contributions.length : 0;

export const getContributionsSectionLabel = contributions => {
    const count = getContributionsCount(contributions);
    return count > 0
        ? `${CONTRIBUTIONS_SECTION_LABEL} (${count})`
        : CONTRIBUTIONS_SECTION_LABEL;
};

export const getUniqueContributorCount = contributions => {
    if (!Array.isArray(contributions) || contributions.length === 0) {
        return 0;
    }
    const definedIds = contributions
        .map(contribution => contribution?.userId)
        .filter(id => id != null);
    const uniqueCount = new Set(definedIds).size;
    return uniqueCount;
};
