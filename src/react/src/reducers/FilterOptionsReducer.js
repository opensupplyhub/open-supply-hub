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
    startFetchTaxonomyCounts,
    startFetchIsic4MappedExtraCount,
    failFetchIsic4MappedExtraCount,
    completeFetchIsic4MappedExtraCount,
    failFetchTaxonomyCounts,
    completeFetchTaxonomyCounts,
    startFetchIsic4TaxonomyConfig,
    failFetchIsic4TaxonomyConfig,
    completeFetchIsic4TaxonomyConfig,
    startFetchIsic4Taxonomy,
    failFetchIsic4Taxonomy,
    completeFetchIsic4Taxonomy,
    startFetchProcessingTypeSuggestions,
    failFetchProcessingTypeSuggestions,
    completeFetchProcessingTypeSuggestions,
    startFetchNumberOfWorkersOptions,
    failFetchNumberOfWorkersOptions,
    completeFetchNumberOfWorkersTypeOptions,
    startFetchClaimStatusOptions,
    failFetchClaimStatusOption,
    completeFetchClaimStatusOption,
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
    taxonomyCounts: Object.freeze({
        isic4: Object.freeze({
            data: null,
            fetching: false,
            error: null,
        }),
        isic4Mapped: Object.freeze({
            data: null,
            fetching: false,
            error: null,
        }),
    }),
    isic4MappedExtraCount: Object.freeze({
        requestKey: null,
        count: null,
        fetching: false,
        error: null,
    }),
    isic4Taxonomy: Object.freeze({
        config: null,
        data: null,
        fetching: false,
        error: null,
    }),
    processingTypeSuggestions: Object.freeze({
        query: null,
        requestIdentity: null,
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
        [startFetchTaxonomyCounts]: (state, kind = 'isic4') =>
            update(state, {
                taxonomyCounts: {
                    [kind]: {
                        fetching: { $set: true },
                        error: { $set: null },
                    },
                },
            }),
        [failFetchTaxonomyCounts]: (state, { kind = 'isic4', error }) =>
            update(state, {
                taxonomyCounts: {
                    [kind]: {
                        fetching: { $set: false },
                        error: { $set: error },
                    },
                },
            }),
        [completeFetchTaxonomyCounts]: (state, { kind = 'isic4', data }) =>
            update(state, {
                taxonomyCounts: {
                    [kind]: {
                        fetching: { $set: false },
                        error: { $set: null },
                        data: { $set: data },
                    },
                },
            }),
        [startFetchIsic4MappedExtraCount]: (state, { requestKey }) =>
            update(state, {
                isic4MappedExtraCount: {
                    $set: {
                        requestKey,
                        count: null,
                        fetching: true,
                        error: null,
                    },
                },
            }),
        [failFetchIsic4MappedExtraCount]: (state, { requestKey, error }) =>
            requestKey !== state.isic4MappedExtraCount.requestKey
                ? state
                : update(state, {
                      isic4MappedExtraCount: {
                          fetching: { $set: false },
                          error: { $set: error },
                      },
                  }),
        [completeFetchIsic4MappedExtraCount]: (state, { requestKey, count }) =>
            requestKey !== state.isic4MappedExtraCount.requestKey
                ? state
                : update(state, {
                      isic4MappedExtraCount: {
                          fetching: { $set: false },
                          count: { $set: count },
                      },
                  }),
        [startFetchIsic4TaxonomyConfig]: state =>
            update(state, {
                isic4Taxonomy: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchIsic4TaxonomyConfig]: (state, payload) =>
            update(state, {
                isic4Taxonomy: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchIsic4TaxonomyConfig]: (state, payload) => {
            const previousVersion = state.isic4Taxonomy.config?.version;
            const versionChanged =
                previousVersion != null && previousVersion !== payload.version;

            return update(state, {
                isic4Taxonomy: {
                    fetching: { $set: false },
                    error: { $set: null },
                    config: { $set: payload },
                    ...(versionChanged ? { data: { $set: null } } : {}),
                },
            });
        },
        [startFetchIsic4Taxonomy]: state =>
            update(state, {
                isic4Taxonomy: {
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        [failFetchIsic4Taxonomy]: (state, payload) =>
            update(state, {
                isic4Taxonomy: {
                    fetching: { $set: false },
                    error: { $set: payload },
                },
            }),
        [completeFetchIsic4Taxonomy]: (state, taxonomy) =>
            update(state, {
                isic4Taxonomy: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: taxonomy },
                },
            }),
        [startFetchProcessingTypeSuggestions]: (
            state,
            { query, requestIdentity },
        ) =>
            update(state, {
                processingTypeSuggestions: {
                    query: { $set: query },
                    requestIdentity: { $set: requestIdentity },
                    fetching: { $set: true },
                    error: { $set: null },
                },
            }),
        /*
        The typeahead fires requests as its query and facility types change, so
        responses can arrive out of order. Anything that does not answer the
        request currently in flight is dropped rather than allowed to overwrite
        fresher results.
        */
        [failFetchProcessingTypeSuggestions]: (
            state,
            { requestIdentity, error },
        ) => {
            if (
                state.processingTypeSuggestions.requestIdentity !==
                requestIdentity
            ) {
                return state;
            }

            return update(state, {
                processingTypeSuggestions: {
                    fetching: { $set: false },
                    error: { $set: error },
                },
            });
        },
        [completeFetchProcessingTypeSuggestions]: (
            state,
            { requestIdentity, data },
        ) => {
            if (
                state.processingTypeSuggestions.requestIdentity !==
                requestIdentity
            ) {
                return state;
            }

            return update(state, {
                processingTypeSuggestions: {
                    fetching: { $set: false },
                    error: { $set: null },
                    data: { $set: data },
                },
            });
        },
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
        [resetFilterOptions]: () => initialState,
    },
    initialState,
);
