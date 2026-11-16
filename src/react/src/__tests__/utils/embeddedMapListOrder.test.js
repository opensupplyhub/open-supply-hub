import {
    EMBED_DEFAULT_SORT,
    EMBED_VISITOR_SORT_OPTIONS,
    formatEmbedConfigForServer,
    formatExistingConfig,
    getDefaultSortOptions,
    hasBlurbField,
} from '../../util/embeddedMap';
import FiltersReducer from '../../reducers/FiltersReducer';
import { resetAllFilters, updateSortAlgorithm } from '../../actions/filters';
import { createQueryStringFromSearchFilters } from '../../util/util';

describe('embedded map list order', () => {
    const fields = [
        { columnName: 'tier', displayName: 'Tier', visible: true, hasData: true },
        {
            columnName: 'parent_company',
            displayName: 'Parent Company',
            visible: true,
            hasData: false,
        },
        {
            columnName: 'hidden',
            displayName: 'Hidden',
            visible: false,
            hasData: true,
        },
    ];

    it('offers name order plus each shown field with data, both ways', () => {
        expect(getDefaultSortOptions(fields).map(o => o.value)).toEqual([
            '',
            'name_desc',
            'field:tier',
            '-field:tier',
        ]);
        expect(getDefaultSortOptions(fields)[2].label).toBe(
            'Tier, lowest first',
        );
    });

    describe('blurbs', () => {
        const withBlurb = [
            ...fields,
            {
                columnName: 'brand_note',
                displayName: 'Brand note',
                visible: true,
                hasData: true,
                displayAs: 'blurb',
            },
        ];

        it('does not offer a blurb as a field to sort by', () => {
            const values = getDefaultSortOptions(withBlurb).map(o => o.value);

            expect(values).not.toContain('field:brand_note');
            expect(values).toContain('field:tier');
        });

        it('knows whether there is a blurb to put first', () => {
            expect(hasBlurbField(withBlurb)).toBe(true);
            expect(hasBlurbField(fields)).toBe(false);
            expect(
                hasBlurbField([{ ...withBlurb[3], visible: false }]),
            ).toBe(false);
            expect(hasBlurbField(undefined)).toBe(false);
        });

        it('maps the blurbs-first setting, off by default', () => {
            expect(formatExistingConfig({ width: '600' }).blurbsFirst).toBe(
                false,
            );
            const config = formatExistingConfig({
                width: '600',
                blurbs_first: true,
            });
            expect(config.blurbsFirst).toBe(true);
            expect(
                formatEmbedConfigForServer(
                    { ...config, fullWidth: false, height: '400' },
                    [],
                ).blurbs_first,
            ).toBe(true);
        });
    });

    it('offers name order alone without fields', () => {
        expect(getDefaultSortOptions(undefined)).toHaveLength(2);
    });

    it('maps the settings to and from the server', () => {
        const config = formatExistingConfig({
            width: '600',
            default_sort: '-field:tier',
            allow_visitor_sort: true,
        });
        expect(config.defaultSort).toBe('-field:tier');
        expect(config.allowVisitorSort).toBe(true);

        const payload = formatEmbedConfigForServer(
            { ...config, fullWidth: false, height: '400' },
            [],
        );
        expect(payload.default_sort).toBe('-field:tier');
        expect(payload.allow_visitor_sort).toBe(true);
    });

    it('defaults to name order and no visitor sorting', () => {
        const config = formatExistingConfig({ width: '600' });
        expect(config.defaultSort).toBe('');
        expect(config.allowVisitorSort).toBe(false);

        const payload = formatEmbedConfigForServer(
            { ...config, fullWidth: false, height: '400' },
            [],
        );
        expect(payload.default_sort).toBeNull();
        expect(payload.allow_visitor_sort).toBe(false);
    });

    it("asks the server for the contributor's order by default", () => {
        expect(EMBED_VISITOR_SORT_OPTIONS[0].value).toBe(EMBED_DEFAULT_SORT);
        expect(
            createQueryStringFromSearchFilters(
                { sortAlgorithm: EMBED_VISITOR_SORT_OPTIONS[0] },
                true,
            ),
        ).toContain('sort_by=embed_default');
    });

    it('keeps the list order through a reset on an embedded map only', () => {
        const sorted = FiltersReducer(
            FiltersReducer(undefined, { type: '@@INIT' }),
            updateSortAlgorithm(EMBED_VISITOR_SORT_OPTIONS[0]),
        );

        expect(
            FiltersReducer(sorted, resetAllFilters(true)).sortAlgorithm,
        ).toEqual(EMBED_VISITOR_SORT_OPTIONS[0]);
        expect(FiltersReducer(sorted, resetAllFilters(false)).sortAlgorithm).toBe(
            '',
        );
    });
});
