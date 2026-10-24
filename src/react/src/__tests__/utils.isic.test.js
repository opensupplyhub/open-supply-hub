/* eslint-env jest */

const {
    createFiltersFromQueryString,
    createQueryStringFromSearchFilters,
    makeGetTaxonomyCountsURL,
} = require('../util/util');

it('creates an ISIC taxonomy counts URL', () => {
    expect(makeGetTaxonomyCountsURL('isic')).toEqual(
        '/api/taxonomy-counts/?kind=isic',
    );
});

it('synchronizes ISIC 4 and ISIC 5 filters with the query string', () => {
    const isic4 = [{ value: 'division:13', label: 'Manufacture of textiles' }];
    const isic5 = [
        { value: 'division:13', label: 'Manufacture of textiles' },
        { value: 'group:631', label: 'Computing infrastructure' },
    ];

    const queryString = createQueryStringFromSearchFilters({ isic4, isic5 });

    expect(queryString).toEqual(
        'isic_4=division%3A13&isic_5=division%3A13&isic_5=group%3A631',
    );
    const filters = createFiltersFromQueryString(`?${queryString}`);
    expect(filters.isic4.map(option => option.value)).toEqual(['division:13']);
    expect(filters.isic5.map(option => option.value)).toEqual([
        'division:13',
        'group:631',
    ]);
});
