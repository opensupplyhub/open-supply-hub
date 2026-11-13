import {
    formatExistingConfig,
    formatEmbedConfigForServer,
} from '../../util/embeddedMap';

describe('embedded map style settings', () => {
    describe('formatExistingConfig', () => {
        it('treats a new config as having no style settings', () => {
            const config = formatExistingConfig(null);

            expect(config.accentColor).toBe('');
            expect(config.headingFont).toBe('');
            expect(config.cornerRadius).toBe('');
        });

        it('treats missing or null values as not set', () => {
            const config = formatExistingConfig({
                width: '600',
                accent_color: null,
                heading_font: null,
                corner_radius: null,
            });

            expect(config.accentColor).toBe('');
            expect(config.headingFont).toBe('');
            expect(config.cornerRadius).toBe('');
        });

        it('reads saved values', () => {
            const config = formatExistingConfig({
                width: '600',
                accent_color: '#f2a900',
                heading_font: 'Georgia,serif',
                corner_radius: 4,
            });

            expect(config.accentColor).toBe('#f2a900');
            expect(config.headingFont).toBe('Georgia,serif');
            expect(config.cornerRadius).toBe(4);
        });

        it('keeps square corners (0) distinct from not set', () => {
            const config = formatExistingConfig({
                width: '600',
                corner_radius: 0,
            });

            expect(config.cornerRadius).toBe(0);
        });
    });

    describe('formatEmbedConfigForServer', () => {
        const base = { width: '600', fullWidth: false, height: '400' };

        it('sends null for settings that are not set', () => {
            const payload = formatEmbedConfigForServer(
                {
                    ...base,
                    accentColor: '',
                    headingFont: '',
                    cornerRadius: '',
                },
                [],
            );

            expect(payload.accent_color).toBeNull();
            expect(payload.heading_font).toBeNull();
            expect(payload.corner_radius).toBeNull();
        });

        it('sends chosen values', () => {
            const payload = formatEmbedConfigForServer(
                {
                    ...base,
                    accentColor: '#f2a900',
                    headingFont: 'Georgia,serif',
                    cornerRadius: 8,
                },
                [],
            );

            expect(payload.accent_color).toBe('#f2a900');
            expect(payload.heading_font).toBe('Georgia,serif');
            expect(payload.corner_radius).toBe(8);
        });

        it('sends 0 for square corners rather than null', () => {
            const payload = formatEmbedConfigForServer(
                { ...base, cornerRadius: 0 },
                [],
            );

            expect(payload.corner_radius).toBe(0);
        });

        it('round-trips a saved config', () => {
            const saved = {
                width: '600',
                height: '400',
                accent_color: '#f2a900',
                heading_font: 'Georgia,serif',
                corner_radius: 0,
            };
            const payload = formatEmbedConfigForServer(
                formatExistingConfig(saved),
                [],
            );

            expect(payload.accent_color).toBe(saved.accent_color);
            expect(payload.heading_font).toBe(saved.heading_font);
            expect(payload.corner_radius).toBe(saved.corner_radius);
        });
    });
});
