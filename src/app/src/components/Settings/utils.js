import includes from 'lodash/includes';
import { EMBEDDED_MAP_FLAG } from '../../util/constants';
import { PROFILE_TAB, EMBED_TAB, API_TAB } from './constants';

/* eslint-disable import/prefer-default-export */
export const getTabs = ({ fetchingFlags, activeFeatureFlags, user }) => {
    if (user.isAnon) return [];

    const removalRange = 1;
    const tabs = [PROFILE_TAB, EMBED_TAB, API_TAB];
    if (fetchingFlags || !includes(activeFeatureFlags, EMBEDDED_MAP_FLAG)) {
        const embedTabIndex = tabs.indexOf(EMBED_TAB);
        tabs.splice(embedTabIndex, removalRange);
    }

    if (!user.groups || user.groups.length === 0) {
        const apiTabIndex = tabs.indexOf(API_TAB);
        tabs.splice(apiTabIndex, removalRange);
    }

    return tabs;
};
