import { embedDrawsDots } from '../../util/embeddedMap';

describe('the switches for changes to every embedded map', () => {
    describe('dots', () => {
        it('are drawn only on an embedded map with the switch on', () => {
            const on = { flags: { embed_facility_dots: true } };
            const off = { flags: { embed_facility_dots: false } };

            expect(embedDrawsDots('1', on)).toBe(true);
            expect(embedDrawsDots('1', off)).toBe(false);
            expect(embedDrawsDots('1', { flags: {} })).toBe(false);
            expect(embedDrawsDots('', on)).toBe(false);
            expect(embedDrawsDots('1', undefined)).toBe(false);
        });
    });
});
