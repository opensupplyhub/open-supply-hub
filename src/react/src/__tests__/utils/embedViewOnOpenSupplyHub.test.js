import { makeProductionLocationPageLink } from '../../util/util';

describe('"View on Open Supply Hub" on an embedded map', () => {
    it("leads to the location's page on Open Supply Hub", () => {
        expect(makeProductionLocationPageLink('VN202631622CV9C')).toBe(
            `${window.location.origin}/production-locations/VN202631622CV9C`,
        );
    });
});
