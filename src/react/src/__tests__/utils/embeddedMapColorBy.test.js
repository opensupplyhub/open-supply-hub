import {
    COLOR_BY_PALETTE,
    formatEmbedConfigForServer,
    formatExistingConfig,
    getColorByLegend,
    getEmbedColorLabel,
    getEmbedColorLegend,
} from '../../util/embeddedMap';

describe('coloring embedded map markers by a field', () => {
    const options = [
        { value: '1', count: 40 },
        { value: '2', count: 12 },
        { value: '3', count: 5 },
    ];

    describe('getColorByLegend', () => {
        it('uses the palette, in order, until a color is chosen', () => {
            expect(getColorByLegend(options, {})).toEqual([
                { value: '1', count: 40, color: COLOR_BY_PALETTE[0] },
                { value: '2', count: 12, color: COLOR_BY_PALETTE[1] },
                { value: '3', count: 5, color: COLOR_BY_PALETTE[2] },
            ]);
        });

        it("prefers the contributor's own colors", () => {
            const legend = getColorByLegend(options, { 2: '#000000' });

            expect(legend[1].color).toBe('#000000');
            expect(legend[0].color).toBe(COLOR_BY_PALETTE[0]);
        });

        it('is empty without values', () => {
            expect(getColorByLegend(undefined, undefined)).toEqual([]);
        });
    });

    describe('embed config', () => {
        const config = {
            color_by_field: 'tier',
            color_by_colors: { 1: '#111111' },
            color_by_options: options,
            embed_fields: [{ column_name: 'tier', display_name: 'Supplier tier' }],
        };

        it('builds the legend for an embed that is colored by a field', () => {
            expect(getEmbedColorLegend(config)[0]).toEqual({
                value: '1',
                count: 40,
                color: '#111111',
            });
            expect(getEmbedColorLabel(config)).toBe('Supplier tier');
        });

        it('has no legend when no field is chosen, or outside an embed', () => {
            expect(getEmbedColorLegend({ ...config, color_by_field: null })).toEqual(
                [],
            );
            expect(getEmbedColorLegend(null)).toEqual([]);
            expect(getEmbedColorLabel(null)).toBe('');
        });

        it('falls back to the column name for the label', () => {
            expect(getEmbedColorLabel({ color_by_field: 'tier' })).toBe('tier');
        });
    });

    describe('settings mapping', () => {
        const base = { width: '600', fullWidth: false, height: '400' };

        it('reads the saved choice', () => {
            const config = formatExistingConfig({
                width: '600',
                color_by_field: 'tier',
                color_by_colors: { 1: '#111111' },
            });

            expect(config.colorByField).toBe('tier');
            expect(config.colorByColors).toEqual({ 1: '#111111' });
        });

        it('treats a missing choice as one color for all', () => {
            const config = formatExistingConfig({ width: '600' });

            expect(config.colorByField).toBe('');
            expect(config.colorByColors).toEqual({});
        });

        it('sends the choice and its colors', () => {
            const payload = formatEmbedConfigForServer(
                { ...base, colorByField: 'tier', colorByColors: { 1: '#111111' } },
                [],
            );

            expect(payload.color_by_field).toBe('tier');
            expect(payload.color_by_colors).toEqual({ 1: '#111111' });
        });

        it('maps a single marker color, defaulting to not set', () => {
            expect(formatExistingConfig({ width: '600' }).markerColor).toBe('');
            expect(
                formatExistingConfig({ width: '600', marker_color: '#c0392b' })
                    .markerColor,
            ).toBe('#c0392b');
            expect(
                formatEmbedConfigForServer(
                    { ...base, markerColor: '#c0392b' },
                    [],
                ).marker_color,
            ).toBe('#c0392b');
            expect(
                formatEmbedConfigForServer({ ...base, markerColor: '' }, [])
                    .marker_color,
            ).toBeNull();
        });

        it('sends no colors when no field is chosen', () => {
            const payload = formatEmbedConfigForServer(
                { ...base, colorByField: '', colorByColors: { 1: '#111111' } },
                [],
            );

            expect(payload.color_by_field).toBeNull();
            expect(payload.color_by_colors).toEqual({});
        });
    });
});
