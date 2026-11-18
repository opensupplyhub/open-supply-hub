/*
 * The production locations a signed-in user opened most recently, for
 * the organization dashboard.
 *
 * Kept in this browser's localStorage, one list per user id, so two
 * accounts sharing a browser do not see each other's history. Nothing
 * is sent to the server, so the list does not follow the user to
 * another browser or device. Storage can be unavailable (private mode,
 * a full quota), so every access is guarded and failure means "no
 * history".
 */

const STORAGE_KEY_PREFIX = 'oshub.recentlyViewedLocations';

export const MAX_RECENTLY_VIEWED = 10;

const storageKey = userID => `${STORAGE_KEY_PREFIX}.${userID}`;

const isLocation = entry =>
    Boolean(entry) &&
    typeof entry.os_id === 'string' &&
    typeof entry.viewed_at === 'string';

export const getRecentlyViewedLocations = userID => {
    if (userID === null || userID === undefined) return [];
    try {
        const stored = JSON.parse(
            window.localStorage.getItem(storageKey(userID)),
        );
        return Array.isArray(stored) ? stored.filter(isLocation) : [];
    } catch (error) {
        return [];
    }
};

/*
 * Puts the location first in the user's list, replacing an earlier view
 * of the same location, and drops the oldest beyond the maximum.
 */
export const recordViewedLocation = (userID, location) => {
    if (userID === null || userID === undefined) return;
    if (!location || !location.os_id) return;

    const entry = {
        os_id: location.os_id,
        name: location.name || '',
        country_name: location.country_name || '',
        viewed_at: location.viewed_at || new Date().toISOString(),
    };
    const others = getRecentlyViewedLocations(userID).filter(
        viewed => viewed.os_id !== entry.os_id,
    );
    try {
        window.localStorage.setItem(
            storageKey(userID),
            JSON.stringify([entry, ...others].slice(0, MAX_RECENTLY_VIEWED)),
        );
    } catch (error) {
        // Nothing to do: the history is a convenience.
    }
};

export const clearRecentlyViewedLocations = userID => {
    try {
        window.localStorage.removeItem(storageKey(userID));
    } catch (error) {
        // Nothing to do.
    }
};
