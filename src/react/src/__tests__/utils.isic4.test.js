/* eslint-env jest */

const {
    createFiltersFromQueryString,
    createQueryStringFromSearchFilters,
    makeGetTaxonomyCountsURL,
} = require('../util/util');

it('creates an ISIC taxonomy counts URL', () => {
    expect(makeGetTaxonomyCountsURL('isic4')).toEqual(
        '/api/taxonomy-counts/?kind=isic4',
    );
});

it('synchronizes ISIC filters with the query string', () => {
    const isic4 = [
        { value: 'section:C', label: 'C - Manufacturing' },
        { value: 'class:0111', label: '0111 - Growing of cereals' },
    ];

    const queryString = createQueryStringFromSearchFilters({ isic4 });

    expect(queryString).toEqual(
        'isic_4=class%3A0111&isic_4=section%3AC',
    );
    expect(createFiltersFromQueryString(`?${queryString}`).isic4).toEqual([
        { value: 'class:0111', label: 'class:0111' },
        { value: 'section:C', label: 'section:C' },
    ]);
});
