import moment from 'moment';
import env from '../env';

import {
    REACT_APP_GOOGLE_ANALYTICS_KEY,
    GA_TRACKING,
    GA_TRACKING_DECISION_DATE,
    HAS_ACCEPTED_GA_TRACKING,
    HAS_REJECTED_GA_TRACKING,
    GA_EVENTS,
} from './constants';

const getCurrentTimestamp = () => moment().toISOString();

const storedConsentIsStillValid = () => {
    try {
        const storedTimestamp = window.localStorage.getItem(
            GA_TRACKING_DECISION_DATE,
        );
        if (!storedTimestamp) {
            throw new Error('no stored timestamp');
        }

        const currentTime = moment();
        const consentExpirationDate = moment(storedTimestamp).add(1, 'years');

        return currentTime.isBefore(consentExpirationDate);
    } catch (e) {
        window.console.warn(e);

        return false;
    }
};

export const maybeGetReactAppGoogleAnalyticsKey = () => {
    const gaKey = env(REACT_APP_GOOGLE_ANALYTICS_KEY);
    const environment = env('ENVIRONMENT');

    if (!environment || environment === 'local') {
        return null;
    }

    return gaKey;
};

export const userHasAcceptedOrRejectedGATracking = () => {
    try {
        if (!storedConsentIsStillValid()) {
            window.localStorage.removeItem(GA_TRACKING);
            window.localStorage.removeItem(GA_TRACKING_DECISION_DATE);

            throw new Error('Consent timestamp is no longer valid');
        }

        return Boolean(window.localStorage.getItem(GA_TRACKING));
    } catch (e) {
        window.console.warn(e);

        return false;
    }
};

export const userHasAcceptedGATracking = () => {
    try {
        if (!storedConsentIsStillValid()) {
            window.localStorage.removeItem(GA_TRACKING);
            window.localStorage.removeItem(GA_TRACKING_DECISION_DATE);

            throw new Error('Consent timestamp is no longer valid');
        }

        return (
            window.localStorage.getItem(GA_TRACKING) ===
            HAS_ACCEPTED_GA_TRACKING
        );
    } catch (e) {
        window.console.warn(e);

        return false;
    }
};

export const userHasRejectedGATracking = () => {
    try {
        return (
            window.localStorage.getItem(GA_TRACKING) ===
            HAS_REJECTED_GA_TRACKING
        );
    } catch (e) {
        window.console.warn(e);

        return false;
    }
};

export const rejectGATracking = () => {
    try {
        window.localStorage.setItem(GA_TRACKING, HAS_REJECTED_GA_TRACKING);
        window.localStorage.setItem(
            GA_TRACKING_DECISION_DATE,
            getCurrentTimestamp(),
        );
    } catch (e) {
        window.console.warn(e);
    }
};

// see https://developers.google.com/analytics/devguides/collection/analyticsjs/user-opt-out
export const createGADisableKey = key => `ga-disable-${key}`;

export const startGATrackingIfUserHasAcceptedNotification = () => {
    try {
        if (
            window.localStorage.getItem(GA_TRACKING) !==
            HAS_ACCEPTED_GA_TRACKING
        ) {
            return null;
        }

        if (!window.localStorage.getItem(GA_TRACKING_DECISION_DATE)) {
            return null;
        }

        const gaKey = maybeGetReactAppGoogleAnalyticsKey();

        if (!gaKey) {
            return null;
        }

        const gaDisableKey = createGADisableKey(gaKey);

        delete window[gaDisableKey];

        /* eslint-disable */
        // Standard gtag.js stub: must assign window.gtag so other modules (e.g.
        // gaCustomEvents) can call it; a function-local `gtag` would not be global.
        window.dataLayer = window.dataLayer || [];
        window.gtag = function gtag() {
            window.dataLayer.push(arguments);
        };
        window.gtag('js', new Date());

        window.gtag(
            'config',
            window.ENVIRONMENT.REACT_APP_GOOGLE_ANALYTICS_KEY,
            {
                anonymize_ip: true,
            },
        );
        /* eslint-enable */

        window.gtag('event', GA_EVENTS.TRACKING_CONSENT, {
            hitType: 'event',
            eventAction: GA_EVENTS.TRACKING_CONSENT,
            eventCategory: GA_EVENTS.TRACKING_CONSENT,
            eventLabel: `User consented to GA tracking on ${window.localStorage.getItem(
                GA_TRACKING_DECISION_DATE,
            )}`, // eslint-disable-line
            nonInteraction: true,
        });

        return 'User clicked Accept on the notification dialog. Google Analytics tracking was started';
    } catch (e) {
        window.console.warn(e);

        return null;
    }
};

export const acceptGATrackingAndStartTracking = () => {
    try {
        // If user has already rejected GA tracking, this is a noop
        if (!userHasRejectedGATracking()) {
            window.localStorage.setItem(GA_TRACKING, HAS_ACCEPTED_GA_TRACKING);
            window.localStorage.setItem(
                GA_TRACKING_DECISION_DATE,
                getCurrentTimestamp(),
            );
            startGATrackingIfUserHasAcceptedNotification();
        }
    } catch (e) {
        window.console.warn(e);
    }
};

export const clearGATrackingDecision = () => {
    try {
        window.localStorage.removeItem(GA_TRACKING);

        // Set the ga-disable property again
        const gaKey = maybeGetReactAppGoogleAnalyticsKey();
        if (gaKey) {
            window[createGADisableKey(gaKey)] = true;
        }
    } catch (e) {
        window.console.warn(e);
    }
};
