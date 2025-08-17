import { createReducer } from 'redux-act';
import update from 'immutability-helper';
import identity from 'lodash/identity';
import orderBy from 'lodash/orderBy';

import {
    updateClaimFacilityIntro,
    startFetchClaimFacilityData,
    failFetchClaimFacilityData,
    completeFetchClaimFacilityData,
    clearClaimFacilityDataAndForm,
    updateClaimAFacilityYourName,
    updateClaimAFacilityYourTitle,
    updateClaimAFacilityYourBusinessWebsite,
    updateClaimAFacilityBusinessWebsite,
    updateClaimAFacilityBusinessLinkedinProfile,
    updateClaimAFacilityClaimReason,
    updateClaimAFacilityClaimReasonOther,
    startFetchClaimsReasons,
    failFetchClaimsReasons,
    completeFetchClaimsReasons,
    updateClaimASector,
    updateClaimANumberOfWorkers,
    updateClaimALocalLanguageName,
    startSubmitClaimAFacilityData,
    failSubmitClaimAFacilityData,
    completeSubmitClaimAFacilityData,
    updateClaimAFacilityUploadFiles,
    updateClaimAFacilityBusinessUploadFiles,
} from '../actions/claimFacility';

const initialState = Object.freeze({
    facilityData: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    claimData: Object.freeze({
        formData: Object.freeze({
            yourName: '',
            yourTitle: '',
            yourBusinessWebsite: '',
            businessWebsite: '',
            businessLinkedinProfile: '',
            claimReason: '',
            claimReasonOther: '',
            sectors: null,
            numberOfWorkers: '',
            localLanguageName: '',
            agreement: 'no',
        }),
        fetching: false,
        error: null,
    }),
    parentCompanyOptions: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    claimsReasons: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [updateClaimFacilityIntro]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        agreement: { $set: payload },
                    },
                },
            }),
        [startFetchClaimFacilityData]: state =>
            update(state, {
                facilityData: {
                    data: { $set: initialState.facilityData.data },
                    fetching: { $set: true },
                    error: { $set: initialState.facilityData.error },
                },
            }),
        [failFetchClaimFacilityData]: (state, error) =>
            update(state, {
                facilityData: {
                    fetching: { $set: false },
                    error: { $set: error },
                },
            }),
        [completeFetchClaimFacilityData]: (state, data) =>
            update(state, {
                facilityData: {
                    data: { $set: data },
                    fetching: { $set: false },
                    error: { $set: initialState.facilityData.error },
                },
            }),
        [updateClaimAFacilityYourName]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        yourName: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityYourTitle]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        yourTitle: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityYourBusinessWebsite]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        yourBusinessWebsite: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityBusinessWebsite]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        businessWebsite: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityBusinessLinkedinProfile]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        businessLinkedinProfile: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityClaimReason]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        claimReason: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityClaimReasonOther]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        claimReasonOther: { $set: payload },
                    },
                },
            }),
        [updateClaimASector]: (state, sectors) =>
            update(state, {
                claimData: {
                    formData: {
                        sectors: {
                            $set: orderBy(sectors, identity),
                        },
                    },
                },
            }),
        [updateClaimANumberOfWorkers]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        numberOfWorkers: { $set: payload },
                    },
                },
            }),
        [updateClaimALocalLanguageName]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        localLanguageName: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityUploadFiles]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        uploadFiles: { $set: payload },
                    },
                },
            }),
        [updateClaimAFacilityBusinessUploadFiles]: (state, payload) =>
            update(state, {
                claimData: {
                    formData: {
                        businessUploadFiles: { $set: payload },
                    },
                },
            }),
        [startSubmitClaimAFacilityData]: state =>
            update(state, {
                claimData: {
                    error: { $set: initialState.claimData.error },
                    fetching: { $set: true },
                },
            }),
        [failSubmitClaimAFacilityData]: (state, error) =>
            update(state, {
                claimData: {
                    error: { $set: error },
                    fetching: { $set: false },
                },
            }),
        [completeSubmitClaimAFacilityData]: state =>
            update(state, {
                claimData: {
                    fetching: { $set: false },
                },
            }),
        [startFetchClaimsReasons]: state =>
            update(state, {
                claimsReasons: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchClaimsReasons]: (state, error) =>
            update(state, {
                claimsReasons: {
                    fetching: { $set: false },
                    error: { $set: error },
                },
            }),
        [completeFetchClaimsReasons]: (state, data) =>
            update(state, {
                claimsReasons: {
                    data: { $set: data.results || data },
                    fetching: { $set: false },
                    error: { $set: null },
                },
            }),
        [clearClaimFacilityDataAndForm]: () => initialState,
    },
    initialState,
);
