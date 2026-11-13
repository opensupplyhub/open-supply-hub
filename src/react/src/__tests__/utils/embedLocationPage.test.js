import {
    getEmbedLocationFields,
    getEmbedLocationPageCss,
    withoutHiddenSector,
} from '../../util/embeddedMap';

describe("a location's page on an embedded map", () => {
    const embedConfig = {
        embed_fields: [
            {
                column_name: 'brand_note',
                display_name: 'Brand note',
                display_as: 'blurb',
                visible: true,
                order: 2,
            },
            {
                column_name: 'tier',
                display_name: 'Tier',
                visible: true,
                order: 0,
            },
            {
                column_name: 'initiatives',
                display_name: 'Initiatives',
                display_as: 'tags',
                visible: true,
                order: 1,
            },
            {
                column_name: 'secret',
                display_name: 'Secret',
                visible: false,
                order: 3,
            },
        ],
    };
    const data = {
        properties: {
            sector: [{ values: ['Apparel'] }],
            contributor_fields: [
                { fieldName: 'tier', value: '3' },
                { fieldName: 'brand_note', value: 'A long partnership.' },
                { fieldName: 'initiatives', value: null },
                { fieldName: 'secret', value: 'x' },
            ],
        },
    };

    describe('the contributor\'s own fields', () => {
        it('are the visible ones with a value, in the chosen order', () => {
            expect(getEmbedLocationFields(embedConfig, data)).toEqual([
                {
                    columnName: 'tier',
                    label: 'Tier',
                    value: '3',
                    displayAs: 'text',
                },
                {
                    columnName: 'brand_note',
                    label: 'Brand note',
                    value: 'A long partnership.',
                    displayAs: 'blurb',
                },
            ]);
        });

        it('are none when there is nothing to show', () => {
            expect(getEmbedLocationFields(embedConfig, null)).toEqual([]);
            expect(getEmbedLocationFields(null, data)).toEqual([]);
            expect(
                getEmbedLocationFields(embedConfig, { properties: {} }),
            ).toEqual([]);
        });
    });

    describe('sector data', () => {
        it('is left out when the contributor hides it', () => {
            const shown = withoutHiddenSector(data, { hide_sector_data: true });

            expect(shown.properties.sector).toEqual([]);
            expect(shown.properties.contributor_fields).toBe(
                data.properties.contributor_fields,
            );
        });

        it('is kept otherwise', () => {
            expect(withoutHiddenSector(data, { hide_sector_data: false })).toBe(
                data,
            );
            expect(withoutHiddenSector(data, null)).toBe(data);
            expect(withoutHiddenSector(null, { hide_sector_data: true })).toBe(
                null,
            );
        });
    });

    describe("the contributor's style", () => {
        it('sets the heading font, accent color and corners', () => {
            const css = getEmbedLocationPageCss({
                accent_color: '#1386c6',
                heading_font: 'Georgia, serif',
                corner_radius: 12,
            });

            expect(css).toContain(
                '.embed-location-page h1, .embed-location-page h2, .embed-location-page h3 { font-family: Georgia, serif !important; }',
            );
            expect(css).toContain('color: #1386c6 !important;');
            expect(css).toContain('border-radius: 12px;');
            expect(css).toContain(
                '.embed-location-page button { border-radius: 12px !important; }',
            );
        });

        it('adds nothing for settings that are not set', () => {
            expect(getEmbedLocationPageCss({})).toBe('');
            expect(getEmbedLocationPageCss(null)).toBe('');
            expect(getEmbedLocationPageCss({ corner_radius: 0 })).toContain(
                'border-radius: 0px;',
            );
        });

        it('ignores values that could break out of a rule', () => {
            expect(
                getEmbedLocationPageCss({
                    accent_color: 'red; } body { display: none',
                    heading_font: 'Arial; } body { display: none',
                }),
            ).toBe('');
        });
    });
});
