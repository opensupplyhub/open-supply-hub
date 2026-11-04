import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchAnnouncementBanner,
    failFetchAnnouncementBanner,
    completeFetchAnnouncementBanner,
} from '../actions/announcementBanner';

const initialState = Object.freeze({
    fetching: false,
    banner: Object.freeze({
        is_active: false,
        content: '',
    }),
});

export default createReducer(
    {
        [startFetchAnnouncementBanner]: state =>
            update(state, {
                fetching: { $set: true },
            }),
        [failFetchAnnouncementBanner]: state =>
            update(state, {
                fetching: { $set: false },
            }),
        [completeFetchAnnouncementBanner]: (state, data) =>
            Object.freeze(
                update(state, {
                    fetching: { $set: false },
                    banner: { $set: data },
                }),
            ),
    },
    initialState,
);
