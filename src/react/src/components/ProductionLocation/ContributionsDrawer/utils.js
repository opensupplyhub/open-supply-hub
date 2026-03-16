import { CONTRIBUTIONS_SECTION_LABEL } from './constants';

export const getContributionsCount = contributions =>
    Array.isArray(contributions) ? contributions.length : 0;

export const getContributionsSectionLabel = contributionsCount =>
    contributionsCount > 0
        ? `${CONTRIBUTIONS_SECTION_LABEL} (${contributionsCount})`
        : CONTRIBUTIONS_SECTION_LABEL;

export const getContributorCount = contributions => {
    if (!Array.isArray(contributions) || contributions.length === 0) {
        return 0;
    }
    const sourceNames = contributions
        .map(contribution => {
            const name = contribution?.sourceName;
            return name != null ? String(name).trim() : name;
        })
        .filter(sourceName => sourceName != null && sourceName !== '');

    const uniqueCount = new Set(sourceNames).size;
    return uniqueCount;
};
