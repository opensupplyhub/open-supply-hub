import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    startFetchContributorOptions,
    failFetchContributorOptions,
    completeFetchContributorOptions,
    startFetchListOptions,
    failFetchListOptions,
    completeFetchListOptions,
    startFetchContributorTypeOptions,
    failFetchContributorTypeOptions,
    completeFetchContributorTypeOptions,
    startFetchCountryOptions,
    failFetchCountryOptions,
    completeFetchCountryOptions,
    startFetchSectorOptions,
    failFetchSectorOptions,
    completeFetchSectorOptions,
    startFetchGroupedSectorOptions,
    failFetchGroupedSectorOptions,
    completeFetchGroupedSectorOptions,
    startFetchParentCompanyOptions,
    failFetchParentCompanyOptions,
    completeFetchParentCompanyOptions,
    startFetchFacilityProcessingTypeOptions,
    failFetchFacilityProcessingTypeOptions,
    completeFetchFacilityProcessingTypeOptions,
    startFetchNumberOfWorkersOptions,
    failFetchNumberOfWorkersOptions,
    completeFetchNumberOfWorkersTypeOptions,
    startFetchClaimStatusOptions,
    failFetchClaimStatusOption,
    completeFetchClaimStatusOption,
    startFetchClaimReasonOptions,
    failFetchClaimReasonOptions,
    completeFetchClaimReasonOptions,
    resetFilterOptions,
} from '../actions/filterOptions';

const initialState = Object.freeze({
    contributors: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    lists: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    contributorTypes: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    countries: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    sectors: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    groupedSectors: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    parentCompanies: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    facilityProcessingType: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    productType: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    numberOfWorkers: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    claimStatuses: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
    claimReasons: Object.freeze({
        data: null,
        fetching: false,
        error: null,
    }),
});

export default createReducer(
    {
        [startFetchContributorOptions]: state =>
            update(state, {
                contributors: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchContributorOptions]: (state, payload) =>
            update(state, {
                contributors: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchContributorOptions]: (state, payload) =>
            update(state, {
                contributors: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchListOptions]: state =>
            update(state, {
                lists: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchListOptions]: (state, payload) =>
            update(state, {
                lists: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchListOptions]: (state, payload) =>
            update(state, {
                lists: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchContributorTypeOptions]: state =>
            update(state, {
                contributorTypes: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchContributorTypeOptions]: (state, payload) =>
            update(state, {
                contributorTypes: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchContributorTypeOptions]: (state, payload) =>
            update(state, {
                contributorTypes: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchCountryOptions]: state =>
            update(state, {
                countries: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchCountryOptions]: (state, payload) =>
            update(state, {
                countries: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchCountryOptions]: (state, payload) =>
            update(state, {
                countries: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchSectorOptions]: state =>
            update(state, {
                sectors: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchSectorOptions]: (state, payload) =>
            update(state, {
                sectors: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchSectorOptions]: (state, payload) =>
            update(state, {
                sectors: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchGroupedSectorOptions]: state =>
            update(state, {
                groupedSectors: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchGroupedSectorOptions]: (state, payload) =>
            update(state, {
                groupedSectors: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchGroupedSectorOptions]: (state, payload) =>
            update(state, {
                groupedSectors: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchParentCompanyOptions]: state =>
            update(state, {
                parentCompanies: {
                    fetching: { $set: true },
                    error: { $set: initialState.parentCompanies.error },
                },
            }),
        [failFetchParentCompanyOptions]: (state, error) =>
            update(state, {
                parentCompanies: {
                    fetching: {
                        $set: initialState.parentCompanies.fetching,
                    },
                    error: { $set: error },
                },
            }),
        [completeFetchParentCompanyOptions]: (state, data) =>
            update(state, {
                parentCompanies: {
                    data: { $set: data },
                    fetching: {
                        $set: initialState.parentCompanies.fetching,
                    },
                },
            }),
        [startFetchFacilityProcessingTypeOptions]: state =>
            update(state, {
                facilityProcessingType: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchFacilityProcessingTypeOptions]: (state, payload) =>
            update(state, {
                facilityProcessingType: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchFacilityProcessingTypeOptions]: (state, payload) =>
            update(state, {
                facilityProcessingType: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchNumberOfWorkersOptions]: state =>
            update(state, {
                numberOfWorkers: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchNumberOfWorkersOptions]: (state, payload) =>
            update(state, {
                numberOfWorkers: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchNumberOfWorkersTypeOptions]: (state, payload) =>
            update(state, {
                numberOfWorkers: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchClaimStatusOptions]: state =>
            update(state, {
                claimStatuses: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchClaimStatusOption]: (state, payload) =>
            update(state, {
                claimStatuses: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchClaimStatusOption]: (state, payload) =>
            update(state, {
                claimStatuses: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [startFetchClaimReasonOptions]: state =>
            update(state, {
                claimReasons: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchClaimReasonOptions]: (state, payload) =>
            update(state, {
                claimReasons: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchClaimReasonOptions]: (state, payload) =>
            update(state, {
                claimReasons: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: payload },
                },
            }),
        [resetFilterOptions]: () => initialState,
    },
    initialState,
);
