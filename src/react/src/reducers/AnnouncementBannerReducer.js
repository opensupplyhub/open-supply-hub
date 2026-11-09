import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    failFetchAnnouncementBanner,
    completeFetchAnnouncementBanner,
} from '../actions/announcementBanner';

const initialState = Object.freeze({
    banner: Object.freeze({
        is_active: false,
        content: '',
    }),
});

export default createReducer(
    {
        [failFetchAnnouncementBanner]: state => state,
        [completeFetchAnnouncementBanner]: (state, data) =>
            Object.freeze(
                update(state, {
                    banner: { $set: data },
                }),
            ),
    },
    initialState,
);
