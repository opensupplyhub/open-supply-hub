import { createAction } from 'redux-act';
import get from 'lodash/get';

import apiRequest from '../util/apiRequest';

import {
    makeAPITokenURL,
    makeUserAPIInfoURL,
    makeUserProfileURL,
    logErrorAndDispatchFailure,
    createProfileUpdateErrorMessages,
    createProfileUpdateRequestData,
} from '../util/util';

export const startFetchAPIToken = createAction('START_FETCH_API_TOKEN');
export const failFetchAPIToken = createAction('FAIL_FETCH_API_TOKEN');
export const completeFetchAPIToken = createAction('COMPLETE_FETCH_API_TOKEN');

export const startDeleteAPIToken = createAction('START_DELETE_API_TOKEN');
export const failDeleteAPIToken = createAction('FAIL_DELETE_API_TOKEN');
export const completeDeleteAPIToken = createAction('COMPLETE_DELETE_API_TOKEN');

export const startCreateAPIToken = createAction('START_CREATE_API_TOKEN');
export const failCreateAPIToken = createAction('FAIL_CREATE_API_TOKEN');
export const completeCreateAPIToken = createAction('COMPLETE_CREATE_API_TOKEN');

export const updateProfileFormInput = createAction('UPDATE_PROFILE_FORM_INPUT');

export const startFetchUserProfile = createAction('START_FETCH_USER_PROFILE');
export const failFetchUserProfile = createAction('FAIL_FETCH_USER_PROFILE');
export const completeFetchUserProfile = createAction(
    'COMPLETE_FETCH_USER_PROFILE',
);
export const completeFetchUserProfileWithEmail = createAction(
    'COMPLETE_FETCH_USER_PROFILE_WITH_EMAIL',
);
export const resetUserProfile = createAction('RESET_USER_PROFILE');

export const startUpdateUserProfile = createAction('START_UPDATE_USER_PROFILE');
export const failUpdateUserProfile = createAction('FAIL_UPDATE_USER_PROFILE');
export const completeUpdateUserProfile = createAction(
    'COMPLETE_UPDATE_USER_PROFILE',
);

export const startFetchUserApiInfo = createAction('START_FETCH_USER_API_INFO');
export const failFetchUserApiInfo = createAction('FAIL_FETCH_USER_API_INFO');
export const completeFetchUserApiInfo = createAction(
    'COMPLETE_FETCH_USER_API_INFO',
);

export function fetchUserApiInfo(uid) {
    return dispatch => {
        dispatch(startFetchUserApiInfo());

        return (
            apiRequest
                .get(makeUserAPIInfoURL(uid))
                // Return user API information
                .then(({ data }) => dispatch(completeFetchUserApiInfo(data)))
                .catch(err =>
                    dispatch(
                        logErrorAndDispatchFailure(
                            err,
                            'An error prevented fetching the API call information',
                            failFetchUserApiInfo,
                        ),
                    ),
                )
        );
    };
}

export function fetchAPIToken() {
    return dispatch => {
        dispatch(startFetchAPIToken());

        return (
            apiRequest
                .get(makeAPITokenURL())
                // Return a list here to afford potentially retrieving and displaying
                // multiple API tokens per user.
                // See https://github.com/open-apparel-registry/open-apparel-registry/issues/119
                .then(({ data }) => dispatch(completeFetchAPIToken([data])))
                .catch(err =>
                    dispatch(
                        logErrorAndDispatchFailure(
                            err,
                            'An error prevented fetching the API token',
                            failFetchAPIToken,
                        ),
                    ),
                )
        );
    };
}

export function deleteAPIToken() {
    return dispatch => {
        dispatch(startDeleteAPIToken());

        return apiRequest
            .delete(makeAPITokenURL())
            .then(() => dispatch(completeDeleteAPIToken()))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented deleting the API token',
                        failDeleteAPIToken,
                    ),
                ),
            );
    };
}

export function createAPIToken() {
    return dispatch => {
        dispatch(startCreateAPIToken());

        return (
            apiRequest
                .post(makeAPITokenURL())
                // Return a list here to afford potentially retrieving and displaying
                // multiple API tokens per user.
                // See https://github.com/open-apparel-registry/open-apparel-registry/issues/119
                .then(({ data }) => dispatch(completeCreateAPIToken([data])))
                .catch(err =>
                    dispatch(
                        logErrorAndDispatchFailure(
                            err,
                            'An error prevented creating an API token',
                            failCreateAPIToken,
                        ),
                    ),
                )
        );
    };
}

export function fetchUserProfile(userID) {
    return (dispatch, getState) => {
        dispatch(startFetchUserProfile());

        if (!userID) {
            return dispatch(
                logErrorAndDispatchFailure(
                    null,
                    'Missing required URL parameter user ID',
                    failFetchUserProfile,
                ),
            );
        }

        const {
            auth: { user },
        } = getState();

        const email = get(user, 'user.email', null);
        const id = get(user, 'user.id', null);

        return apiRequest
            .get(makeUserProfileURL(userID))
            .then(({ data }) => {
                if (id === userID && id === data.id) {
                    const dataWithEmail = Object.assign({}, data, { email });
                    return dispatch(
                        completeFetchUserProfileWithEmail(dataWithEmail),
                    );
                }

                return dispatch(completeFetchUserProfile(data));
            })
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented fetching user profile data',
                        failFetchUserProfile,
                    ),
                ),
            );
    };
}

export function updateUserProfile(userID) {
    return (dispatch, getState) => {
        dispatch(startUpdateUserProfile());

        const {
            profile: { profile },
        } = getState();

        if (!profile.id || !userID || profile.id !== userID) {
            // in this case it's not an editable profile, so provide a terse error message
            return dispatch(
                logErrorAndDispatchFailure(
                    null,
                    'An error prevented updating profile data',
                    failUpdateUserProfile,
                ),
            );
        }

        const missingRequiredFieldMessages = createProfileUpdateErrorMessages(
            profile,
        );

        if (missingRequiredFieldMessages.length) {
            return dispatch(
                failUpdateUserProfile(missingRequiredFieldMessages),
            );
        }

        const profileUpdateData = createProfileUpdateRequestData(profile);

        return apiRequest
            .put(makeUserProfileURL(userID), profileUpdateData)
            .then(({ data }) => dispatch(completeUpdateUserProfile(data)))
            .catch(err =>
                dispatch(
                    logErrorAndDispatchFailure(
                        err,
                        'An error prevented updating profile data',
                        failUpdateUserProfile,
                    ),
                ),
            );
    };
}
