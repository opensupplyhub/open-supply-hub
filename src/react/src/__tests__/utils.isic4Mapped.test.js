/* eslint-env jest */

const {
    createFiltersFromQueryString,
    createQueryStringFromSearchFilters,
    makeGetIsic4MappedExtraCountURL,
    makeGetTaxonomyCountsURL,
} = require('../util/util');
const { ISIC4_MAPPED_COUNTS_KIND } = require('../util/constants');

const isic4 = [{ value: 'section:C', label: 'section:C' }];

it('creates the counts URL that includes mapped values', () => {
    expect(makeGetTaxonomyCountsURL(ISIC4_MAPPED_COUNTS_KIND)).toEqual(
        '/api/taxonomy-counts/?kind=isic4&include_mapped=true',
    );
    expect(makeGetTaxonomyCountsURL('isic4')).toEqual(
        '/api/taxonomy-counts/?kind=isic4',
    );
});

it('creates a stable extra-count URL for a selection', () => {
    expect(
        makeGetIsic4MappedExtraCountURL([
            { value: 'section:C' },
            { value: 'class:1410' },
        ]),
    ).toEqual(
        '/api/taxonomy-counts/?kind=isic4_mapped_extra&isic_4=class%3A1410&isic_4=section%3AC',
    );
});

it('adds the opt-in to the query string only with an ISIC selection', () => {
    expect(
        createQueryStringFromSearchFilters({
            isic4,
            isic4IncludeMapped: true,
        }),
    ).toEqual('isic_4=section%3AC&isic_4_include_mapped=true');
    expect(
        createQueryStringFromSearchFilters({ isic4IncludeMapped: true }),
    ).toEqual('');
    expect(
        createQueryStringFromSearchFilters({
            isic4,
            isic4IncludeMapped: false,
        }),
    ).toEqual('isic_4=section%3AC');
});

it('restores the opt-in from the query string', () => {
    expect(
        createFiltersFromQueryString(
            '?isic_4=section%3AC&isic_4_include_mapped=true',
        ).isic4IncludeMapped,
    ).toBe(true);
    expect(
        createFiltersFromQueryString('?isic_4=section%3AC').isic4IncludeMapped,
    ).toBe(false);
});
