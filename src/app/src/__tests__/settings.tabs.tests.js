/* eslint-env jest */
const {getTabs} = require('../components/Settings/utils');
const { PROFILE_TAB, EMBED_TAB, API_TAB } = require('../components/Settings/constants');
const { EMBEDDED_MAP_FLAG } = require('../util/constants');

it('get tabs when anon user', () => {
    const fetchingFlags = false;
    const activeFeatureFlags = [];
    const user = { isAnon: true };

    const tabs = getTabs({fetchingFlags, activeFeatureFlags, user});

    expect(tabs).toStrictEqual([]);
});

it('get tabs when fetching flags and user groups empty', () => {
    const fetchingFlags = true;
    const activeFeatureFlags = [];
    const user = { isAnon: false, groups: [] };

    const tabs = getTabs({fetchingFlags, activeFeatureFlags, user});

    expect(tabs).toStrictEqual([PROFILE_TAB])
});

it('get tabs when feature flags exist and user groups empty', () => {
    const fetchingFlags = false;
    const activeFeatureFlags = [EMBEDDED_MAP_FLAG];
    const user = { isAnon: false, groups: [] };

    const tabs = getTabs({fetchingFlags, activeFeatureFlags, user});

    expect(tabs).toStrictEqual([PROFILE_TAB, EMBED_TAB]);
});

it('get tabs when user has groups', () => {
    const fetchingFlags = false;
    const activeFeatureFlags = [EMBEDDED_MAP_FLAG];
    const user = { isAnon: false, groups: [1,2,3,4] };

    const tabs = getTabs({fetchingFlags, activeFeatureFlags, user});

    expect(tabs).toStrictEqual([PROFILE_TAB, EMBED_TAB, API_TAB]);
});

it('get tabs when feature flags exist and user has groups', () => {
    const fetchingFlags = false;
    const activeFeatureFlags = [];
    const user = { isAnon: false, groups: [1,2,3,4] };

    const tabs = getTabs({fetchingFlags, activeFeatureFlags, user});

    expect(tabs).toStrictEqual([PROFILE_TAB, API_TAB]);
});