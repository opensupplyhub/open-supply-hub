/* eslint-env jest */
import {
    MAX_RECENTLY_VIEWED,
    clearRecentlyViewedLocations,
    getRecentlyViewedLocations,
    recordViewedLocation,
} from '../../components/Organization/recentlyViewed';

const location = (osID, overrides = {}) => ({
    os_id: osID,
    name: `Location ${osID}`,
    country_name: 'India',
    ...overrides,
});

describe('recently viewed production locations', () => {
    beforeEach(() => {
        window.localStorage.clear();
    });

    test('starts empty', () => {
        expect(getRecentlyViewedLocations(7)).toEqual([]);
    });

    test('keeps the newest first and one entry per location', () => {
        recordViewedLocation(7, location('A', { viewed_at: '2026-11-01T10:00:00Z' }));
        recordViewedLocation(7, location('B', { viewed_at: '2026-11-02T10:00:00Z' }));
        recordViewedLocation(7, location('A', { viewed_at: '2026-11-03T10:00:00Z' }));

        const viewed = getRecentlyViewedLocations(7);
        expect(viewed.map(entry => entry.os_id)).toEqual(['A', 'B']);
        expect(viewed[0].viewed_at).toBe('2026-11-03T10:00:00Z');
        expect(viewed[0].name).toBe('Location A');
    });

    test('drops the oldest beyond the maximum', () => {
        for (let index = 0; index < MAX_RECENTLY_VIEWED + 3; index += 1) {
            recordViewedLocation(7, location(`L${index}`));
        }

        const viewed = getRecentlyViewedLocations(7);
        expect(viewed).toHaveLength(MAX_RECENTLY_VIEWED);
        expect(viewed[0].os_id).toBe(`L${MAX_RECENTLY_VIEWED + 2}`);
    });

    test('keeps a separate list for each user', () => {
        recordViewedLocation(7, location('A'));
        recordViewedLocation(8, location('B'));

        expect(getRecentlyViewedLocations(7).map(e => e.os_id)).toEqual(['A']);
        expect(getRecentlyViewedLocations(8).map(e => e.os_id)).toEqual(['B']);

        clearRecentlyViewedLocations(7);
        expect(getRecentlyViewedLocations(7)).toEqual([]);
        expect(getRecentlyViewedLocations(8)).toHaveLength(1);
    });

    test('records nothing without a user or a location id', () => {
        recordViewedLocation(null, location('A'));
        recordViewedLocation(7, { name: 'No id' });
        recordViewedLocation(7, null);

        expect(getRecentlyViewedLocations(null)).toEqual([]);
        expect(getRecentlyViewedLocations(7)).toEqual([]);
    });

    test('ignores stored data that is not a list of locations', () => {
        window.localStorage.setItem(
            'oshub.recentlyViewedLocations.7',
            '{"not": "a list"}',
        );
        expect(getRecentlyViewedLocations(7)).toEqual([]);

        window.localStorage.setItem(
            'oshub.recentlyViewedLocations.7',
            'not json',
        );
        expect(getRecentlyViewedLocations(7)).toEqual([]);

        window.localStorage.setItem(
            'oshub.recentlyViewedLocations.7',
            JSON.stringify([{ os_id: 'A', viewed_at: '2026-11-01' }, { bad: 1 }]),
        );
        expect(getRecentlyViewedLocations(7).map(e => e.os_id)).toEqual(['A']);
    });
});
