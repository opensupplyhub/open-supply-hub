import {
    ANY_SPOTLIGHT,
    EMBED_SPOTLIGHT_FILTER,
    formatEmbedConfigForServer,
    formatExistingConfig,
    getEmbedSpotlight,
    getSpotlightFieldNames,
    getSpotlightFilterOptions,
    getSpotlightRingColor,
    getSpotlightTileKey,
    keepShownPartnerFields,
    toggleSpotlightGroup,
} from '../../util/embeddedMap';
import {
    createQueryStringFromSearchFilters,
    formatEmbedFiltersForQueryString,
    createFiltersFromQueryString,
} from '../../util/util';
import FiltersReducer from '../../reducers/FiltersReducer';

describe('Spotlight on an embedded map', () => {
    const spotlight = {
        highlight: true,
        filter: true,
        count: 14,
        groups: [
            {
                uuid: '1eae7311-08d0-428f-87d2-36fa1c790b79',
                name: 'Environmental assessment',
                count: 13,
                field_names: ['env_assessment'],
            },
            {
                uuid: 'ab97b276-875d-472d-b950-868c7c2de68d',
                name: 'Worker voice program',
                count: 0,
                field_names: ['worker_voice', 'helpline'],
            },
        ],
    };

    it('is only read on an embedded map whose contributor shows it', () => {
        expect(getEmbedSpotlight(true, { spotlight })).toBe(spotlight);
        expect(getEmbedSpotlight(false, { spotlight })).toBeNull();
        expect(getEmbedSpotlight(true, { spotlight: null })).toBeNull();
        expect(getEmbedSpotlight(true, null)).toBeNull();
    });

    describe('the filter', () => {
        it('offers any data, then each kind that a facility has', () => {
            expect(getSpotlightFilterOptions(spotlight)).toEqual([
                { value: ANY_SPOTLIGHT, label: 'Any partner data (14)' },
                {
                    value: '1eae7311-08d0-428f-87d2-36fa1c790b79',
                    label: 'Environmental assessment (13)',
                },
            ]);
        });

        it('is not offered unless the contributor offers it', () => {
            expect(
                getSpotlightFilterOptions({ ...spotlight, filter: false }),
            ).toEqual([]);
            expect(
                getSpotlightFilterOptions({ ...spotlight, count: 0 }),
            ).toEqual([]);
            expect(getSpotlightFilterOptions(null)).toEqual([]);
        });

        it('travels on its own, apart from the column filters', () => {
            const embedFilters = {
                tier: '1',
                [EMBED_SPOTLIGHT_FILTER]: ANY_SPOTLIGHT,
            };

            expect(formatEmbedFiltersForQueryString(embedFilters)).toEqual([
                'tier::1',
            ]);

            const initial = FiltersReducer(undefined, { type: '@@INIT' });
            const filters = { ...initial, embedFilters };
            const embedded = createQueryStringFromSearchFilters(filters, true);
            expect(embedded).toContain('embed_spotlight=any');
            expect(embedded).not.toContain('__spotlight__');
            expect(
                createQueryStringFromSearchFilters(filters, false),
            ).not.toContain('embed_spotlight');
        });

        it('is read back from a link to the map', () => {
            const { embedFilters } = createFiltersFromQueryString(
                '?embed=1&embed_filters=tier::1&embed_spotlight=any',
            );

            expect(embedFilters).toEqual({
                tier: '1',
                [EMBED_SPOTLIGHT_FILTER]: ANY_SPOTLIGHT,
            });
            expect(
                createFiltersFromQueryString('?embed=1').embedFilters,
            ).toEqual({});
        });
    });

    describe('the map', () => {
        it('asks for flagged tiles only when facilities are ringed', () => {
            expect(getSpotlightTileKey(spotlight)).toBe('1eae7311.ab97b276');
            expect(
                getSpotlightTileKey({ ...spotlight, highlight: false }),
            ).toBe('');
            expect(getSpotlightTileKey(null)).toBe('');
        });

        it('rings in the accent color, else the primary color', () => {
            expect(
                getSpotlightRingColor({ accent_color: '#111', color: '#222' }),
            ).toBe('#111');
            expect(getSpotlightRingColor({ color: '#222' })).toBe('#222');
            expect(getSpotlightRingColor(null)).toBe('#0D1128');
        });
    });

    describe('a facility\'s details', () => {
        it('keep only the partner data the map shows', () => {
            const data = {
                properties: {
                    name: 'Factory',
                    partner_fields: {
                        env_assessment: [{ value: 'Done' }],
                        other_partner_field: [{ value: 'Hidden' }],
                    },
                },
            };

            expect(getSpotlightFieldNames(spotlight)).toEqual([
                'env_assessment',
                'worker_voice',
                'helpline',
            ]);
            expect(
                keepShownPartnerFields(data, spotlight).properties,
            ).toEqual({
                name: 'Factory',
                partner_fields: { env_assessment: [{ value: 'Done' }] },
            });
            expect(
                keepShownPartnerFields(data, null).properties.partner_fields,
            ).toEqual({});
        });
    });

    describe('the settings', () => {
        it('are off until the contributor turns them on', () => {
            expect(formatExistingConfig(null)).toMatchObject({
                showSpotlight: false,
                spotlightHighlight: false,
                spotlightFilter: false,
                spotlightGroups: [],
            });
            expect(
                formatExistingConfig({
                    show_spotlight: true,
                    spotlight_highlight: true,
                    spotlight_filter: false,
                    spotlight_groups: ['a'],
                }),
            ).toMatchObject({
                showSpotlight: true,
                spotlightHighlight: true,
                spotlightFilter: false,
                spotlightGroups: ['a'],
            });
        });

        it('are sent to the server', () => {
            expect(
                formatEmbedConfigForServer(
                    {
                        showSpotlight: true,
                        spotlightHighlight: false,
                        spotlightFilter: true,
                        spotlightGroups: ['a', 'b'],
                    },
                    [],
                ),
            ).toMatchObject({
                show_spotlight: true,
                spotlight_highlight: false,
                spotlight_filter: true,
                spotlight_groups: ['a', 'b'],
            });
        });

        it('tick and untick a kind of data', () => {
            expect(toggleSpotlightGroup(['a'], 'b', true)).toEqual(['a', 'b']);
            expect(toggleSpotlightGroup(['a', 'b'], 'a', false)).toEqual(['b']);
            expect(toggleSpotlightGroup(['a'], 'a', true)).toEqual(['a']);
        });
    });
});
