import {
    embedUsesProductionLocationPage,
    cleanValueDescriptions,
    formatEmbedConfigForServer,
    formatExistingFields,
    getValueExplanations,
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
                    description: '',
                    explanations: [],
                },
                {
                    columnName: 'brand_note',
                    label: 'Brand note',
                    value: 'A long partnership.',
                    displayAs: 'blurb',
                    description: '',
                    explanations: [],
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

    describe("the contributor's explanations", () => {
        const explained = {
            embed_fields: [
                {
                    column_name: 'initiatives',
                    display_name: 'Initiatives',
                    display_as: 'tags',
                    visible: true,
                    order: 0,
                    description: 'Programs this facility takes part in.',
                    value_descriptions: {
                        'Planet Water Foundation': 'Clean water access.',
                        RISE: 'Workplace equality training.',
                        Unused: 'Not on this location.',
                    },
                },
                {
                    column_name: 'brand_note',
                    display_name: 'Brand note',
                    display_as: 'blurb',
                    visible: true,
                    order: 1,
                    value_descriptions: { 'A note': 'Never shown.' },
                },
            ],
        };
        const location = {
            properties: {
                contributor_fields: [
                    {
                        fieldName: 'initiatives',
                        value: 'HERhealth|planet water foundation | RISE',
                    },
                    { fieldName: 'brand_note', value: 'A note' },
                ],
            },
        };

        it('go with the field, for the values this location has', () => {
            const [initiatives, note] = getEmbedLocationFields(
                explained,
                location,
            );

            expect(initiatives.description).toBe(
                'Programs this facility takes part in.',
            );
            expect(initiatives.explanations).toEqual([
                {
                    value: 'planet water foundation',
                    text: 'Clean water access.',
                },
                { value: 'RISE', text: 'Workplace equality training.' },
            ]);
            // A blurb is free text, not a value to look up.
            expect(note.explanations).toEqual([]);
        });

        it('match values whatever their case, and skip unexplained ones', () => {
            expect(
                getValueExplanations('rise, Other', { RISE: 'Training.' }),
            ).toEqual([{ value: 'rise', text: 'Training.' }]);
            expect(getValueExplanations('RISE', {})).toEqual([]);
            expect(getValueExplanations('RISE', undefined)).toEqual([]);
        });

        it('are sent to the server without the empty ones', () => {
            expect(
                cleanValueDescriptions({
                    RISE: ' Training. ',
                    HERhealth: '   ',
                    Other: '',
                }),
            ).toEqual({ RISE: 'Training.' });

            const [sent] = formatEmbedConfigForServer({}, [
                {
                    columnName: 'initiatives',
                    displayName: 'Initiatives',
                    visible: true,
                    order: 0,
                    description: ' Programs. ',
                    valueDescriptions: { RISE: 'Training.', Other: ' ' },
                },
            ]).embed_fields;

            expect(sent.description).toBe('Programs.');
            expect(sent.value_descriptions).toEqual({ RISE: 'Training.' });
        });

        it('are read back from the server', () => {
            const [field] = formatExistingFields([
                {
                    column_name: 'initiatives',
                    display_name: 'Initiatives',
                    description: 'Programs.',
                    value_descriptions: { RISE: 'Training.' },
                },
            ]);

            expect(field.description).toBe('Programs.');
            expect(field.valueDescriptions).toEqual({ RISE: 'Training.' });
            expect(
                formatExistingFields([{ column_name: 'tier' }])[0],
            ).toMatchObject({ description: '', valueDescriptions: {} });
        });
    });

    it('is only used by an embedded map while its switch is on', () => {
        const on = { flags: { embed_production_location_page: true } };

        expect(embedUsesProductionLocationPage('1', on)).toBe(true);
        expect(
            embedUsesProductionLocationPage('1', {
                flags: { embed_production_location_page: false },
            }),
        ).toBe(false);
        // The main site's own switch for the page does not turn it on.
        expect(
            embedUsesProductionLocationPage('1', {
                flags: { enable_production_location_page: true },
            }),
        ).toBe(false);
        expect(embedUsesProductionLocationPage('', on)).toBe(false);
        expect(embedUsesProductionLocationPage('1', undefined)).toBe(false);
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
