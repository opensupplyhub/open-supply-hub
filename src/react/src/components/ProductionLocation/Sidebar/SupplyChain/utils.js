import PLURAL_MAP from './constants';

export const buildTypeCounts = contributors => {
    const totals = contributors.reduce((acc, contributor) => {
        const type = contributor.contributor_type;
        if (!type) return acc;
        const count = contributor.count || 1;
        acc[type] = (acc[type] || 0) + count;
        return acc;
    }, {});

    return Object.entries(totals).map(([type, count]) => ({ type, count }));
};

export const aggregateByType = nonPublicContributors =>
    nonPublicContributors
        .filter(c => c.contributor_type != null)
        .reduce((acc, c) => {
            const existing = acc.find(
                x => x.contributor_type === c.contributor_type,
            );
            if (existing) {
                return acc.map(item =>
                    item.contributor_type === c.contributor_type
                        ? { ...item, count: item.count + (c.count || 1) }
                        : item,
                );
            }
            return [
                ...acc,
                {
                    contributor_type: c.contributor_type,
                    count: c.count || 1,
                },
            ];
        }, []);

export const getTotalCount = contributors =>
    contributors.reduce((sum, c) => sum + (c.count || 1), 0);

export const pluralizeContributorType = (type, count) => {
    if (count === 1) return type;
    return PLURAL_MAP[type] || `${type}s`;
};
