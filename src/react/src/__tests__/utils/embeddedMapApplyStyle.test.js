import {
    embedCornerStyle,
    embedHeadingFont,
    getEmbedStyle,
    themeEmbedStyle,
} from '../../util/embeddedMap';

const NOT_SET = { accentColor: null, headingFont: null, cornerRadius: null };

describe('applying embedded map style settings', () => {
    describe('getEmbedStyle', () => {
        const config = {
            color: '#000000',
            accent_color: '#f2a900',
            heading_font: 'Georgia,serif',
            corner_radius: 8,
        };

        it('returns the saved settings in embed mode', () => {
            expect(getEmbedStyle(true, config)).toEqual({
                accentColor: '#f2a900',
                headingFont: 'Georgia,serif',
                cornerRadius: 8,
            });
        });

        it('ignores the settings outside embed mode', () => {
            expect(getEmbedStyle(false, config)).toEqual(NOT_SET);
        });

        it('treats missing and null settings as not set', () => {
            expect(getEmbedStyle(true, { color: '#000000' })).toEqual(NOT_SET);
            expect(
                getEmbedStyle(true, {
                    accent_color: null,
                    heading_font: null,
                    corner_radius: null,
                }),
            ).toEqual(NOT_SET);
        });

        it('keeps square corners (0) distinct from not set', () => {
            expect(getEmbedStyle(true, { corner_radius: 0 }).cornerRadius).toBe(
                0,
            );
        });
    });

    describe('theme helpers', () => {
        const typography = { fontFamily: 'Arial' };

        it('fall back to the component style when nothing is set', () => {
            const theme = { typography };

            expect(themeEmbedStyle(theme)).toEqual(NOT_SET);
            expect(embedHeadingFont(theme)).toBe('Arial');
            expect(embedCornerStyle(theme)).toEqual({});
        });

        it('use the embed style when it is set', () => {
            const theme = {
                typography,
                embed: {
                    accentColor: '#f2a900',
                    headingFont: 'Georgia,serif',
                    cornerRadius: 0,
                },
            };

            expect(embedHeadingFont(theme)).toBe('Georgia,serif');
            expect(embedCornerStyle(theme)).toEqual({ borderRadius: '0px' });
        });
    });
});
