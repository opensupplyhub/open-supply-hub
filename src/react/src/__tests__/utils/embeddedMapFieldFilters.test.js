import {
    formatEmbedConfigForServer,
    formatExistingFields,
    getEmbedFieldFilters,
} from '../../util/embeddedMap';
import {
    createFiltersFromQueryString,
    createQueryStringFromSearchFilters,
    formatEmbedFiltersForQueryString,
    parseEmbedFiltersFromQueryString,
} from '../../util/util';
import FiltersReducer from '../../reducers/FiltersReducer';
import { resetAllFilters, updateEmbedFilter } from '../../actions/filters';

describe('embedded map filters on a contributor\'s own columns', () => {
    const embedFields = [
        {
            column_name: 'tier',
            display_name: 'Tier',
            visible: true,
            filterable: true,
            order: 1,
        },
        {
            column_name: 'project',
            display_name: 'Programs',
            visible: true,
            filterable: true,
            order: 0,
        },
        {
            column_name: 'hidden',
            display_name: 'Hidden',
            visible: false,
            filterable: true,
            order: 2,
        },
        {
            column_name: 'parent_company',
            display_name: 'Parent Company',
            visible: true,
            filterable: false,
            order: 3,
        },
        {
            column_name: 'empty',
            display_name: 'Empty',
            visible: true,
            filterable: true,
            order: 4,
        },
    ];
    const filterOptions = {
        tier: [
            { value: '1', count: 40 },
            { value: '2', count: 12 },
        ],
        project: [{ value: 'HERhealth', count: 17 }],
        hidden: [{ value: 'x', count: 1 }],
        empty: [],
    };

    describe('getEmbedFieldFilters', () => {
        it('offers visible, filterable fields that have values, in order', () => {
            const filters = getEmbedFieldFilters(embedFields, filterOptions);

            expect(filters.map(f => f.columnName)).toEqual(['project', 'tier']);
            expect(filters[0].label).toBe('Programs');
            expect(filters[1].options).toEqual([
                { value: '1', label: '1 (40)' },
                { value: '2', label: '2 (12)' },
            ]);
        });

        it('offers nothing without a config', () => {
            expect(getEmbedFieldFilters(undefined, undefined)).toEqual([]);
            expect(getEmbedFieldFilters(embedFields, undefined)).toEqual([]);
        });
    });

    describe('settings mapping', () => {
        it('reads and sends the filterable flag', () => {
            const [field] = formatExistingFields([embedFields[0]]);
            expect(field.filterable).toBe(true);

            const payload = formatEmbedConfigForServer(
                { width: '600', fullWidth: false, height: '400' },
                [{ ...field, order: 0 }],
            );
            expect(payload.embed_fields[0].filterable).toBe(true);
        });

        it('defaults to not filterable', () => {
            const [field] = formatExistingFields([
                { column_name: 'x', display_name: 'X', visible: true, order: 0 },
            ]);
            expect(field.filterable).toBe(false);
        });
    });

    describe('query string', () => {
        it('formats each filter as column::value, sorted', () => {
            expect(
                formatEmbedFiltersForQueryString({ tier: '1', project: 'RISE' }),
            ).toEqual(['project::RISE', 'tier::1']);
        });

        it('leaves out empty filters', () => {
            expect(formatEmbedFiltersForQueryString({ tier: '' })).toEqual([]);
            expect(formatEmbedFiltersForQueryString(undefined)).toEqual([]);
        });

        it('parses one or many filters and skips malformed ones', () => {
            expect(parseEmbedFiltersFromQueryString('tier::1')).toEqual({
                tier: '1',
            });
            expect(
                parseEmbedFiltersFromQueryString([
                    'tier::1',
                    'project::Clean by Design',
                    'broken',
                    '::x',
                    'tier2::',
                ]),
            ).toEqual({ tier: '1', project: 'Clean by Design' });
            expect(parseEmbedFiltersFromQueryString(undefined)).toEqual({});
        });

        it('is only sent in embed mode', () => {
            const filters = { embedFilters: { tier: '1' } };

            expect(createQueryStringFromSearchFilters(filters, true)).toContain(
                'embed_filters=tier%3A%3A1',
            );
            expect(
                createQueryStringFromSearchFilters(filters, false),
            ).not.toContain('embed_filters');
        });

        it('round-trips through the URL', () => {
            const qs = createQueryStringFromSearchFilters(
                { embedFilters: { tier: '2', project: 'HERhealth' } },
                true,
            );

            expect(createFiltersFromQueryString(qs).embedFilters).toEqual({
                tier: '2',
                project: 'HERhealth',
            });
        });
    });

    describe('reducer', () => {
        const initial = FiltersReducer(undefined, { type: '@@INIT' });

        it('starts with no embed filters', () => {
            expect(initial.embedFilters).toEqual({});
        });

        it('sets, replaces and clears a filter', () => {
            let state = FiltersReducer(
                initial,
                updateEmbedFilter({ column: 'tier', value: '1' }),
            );
            state = FiltersReducer(
                state,
                updateEmbedFilter({ column: 'project', value: 'RISE' }),
            );
            expect(state.embedFilters).toEqual({ tier: '1', project: 'RISE' });

            state = FiltersReducer(
                state,
                updateEmbedFilter({ column: 'tier', value: '2' }),
            );
            expect(state.embedFilters.tier).toBe('2');

            state = FiltersReducer(
                state,
                updateEmbedFilter({ column: 'tier', value: '' }),
            );
            expect(state.embedFilters).toEqual({ project: 'RISE' });
        });

        it('is cleared by a filter reset', () => {
            const state = FiltersReducer(
                FiltersReducer(
                    initial,
                    updateEmbedFilter({ column: 'tier', value: '1' }),
                ),
                resetAllFilters(true),
            );
            expect(state.embedFilters).toEqual({});
        });
    });
});
