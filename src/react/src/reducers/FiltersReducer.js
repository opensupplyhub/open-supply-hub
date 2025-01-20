import { createReducer } from 'redux-act';
import update from 'immutability-helper';

import {
    updateFacilityFreeTextQueryFilter,
    updateContributorFilter,
    updateListFilter,
    updateContributorTypeFilter,
    updateCountryFilter,
    clearCountryFilter,
    updateClaimStatusFilter,
    updateSectorFilter,
    updateParentCompanyFilter,
    updateFacilityTypeFilter,
    updateProcessingTypeFilter,
    updateProductTypeFilter,
    updateNumberofWorkersFilter,
    updateNativeLanguageNameFilter,
    updateSortAlgorithm,
    updateCombineContributorsFilterOption,
    updateBoundaryFilter,
    resetAllFilters,
    resetDrawerFilters,
    updateAllFilters,
    updateDataSourceFilter,
    updateModerationStatusFilter,
} from '../actions/filters';

import {
    completeFetchContributorOptions,
    completeFetchContributorTypeOptions,
    completeFetchCountryOptions,
    completeFetchSectorOptions,
    completeFetchParentCompanyOptions,
    completeFetchGroupedSectorOptions,
} from '../actions/filterOptions';

import { completeSubmitLogOut } from '../actions/auth';

import { updateListWithLabels } from '../util/util';

const initialState = Object.freeze({
    facilityFreeTextQuery: '',
    contributors: Object.freeze([]),
    contributorTypes: Object.freeze([]),
    countries: Object.freeze([]),
    claimStatuses: Object.freeze([]),
    sectors: Object.freeze([]),
    sortAlgorithm: '',
    parentCompany: Object.freeze([]),
    facilityType: Object.freeze([]),
    processingType: Object.freeze([]),
    productType: Object.freeze([]),
    numberOfWorkers: Object.freeze([]),
    dataSources: Object.freeze([]),
    moderationStatuses: Object.freeze([]),
    nativeLanguageName: '',
    combineContributors: '',
    boundary: null,
    lists: Object.freeze([]),
});

export const maybeSetFromQueryString = field => (state, payload) => {
    if (!state[field].length) {
        return state;
    }

    // filter out any options set from the querystring which turn out
    // not to be valid according to the API's response
    const updatedField = updateListWithLabels(state[field], payload);

    return update(state, {
        [field]: { $set: updatedField },
    });
};

export default createReducer(
    {
        [updateFacilityFreeTextQueryFilter]: (state, payload) =>
            update(state, {
                facilityFreeTextQuery: { $set: payload },
            }),
        [updateContributorFilter]: (state, payload) =>
            update(state, {
                contributors: { $set: payload },
                lists: { $set: initialState.lists },
            }),
        [updateContributorTypeFilter]: (state, payload) =>
            update(state, {
                contributorTypes: { $set: payload },
            }),
        [updateCountryFilter]: (state, payload) =>
            update(state, {
                countries: { $set: payload },
            }),
        [clearCountryFilter]: state =>
            update(state, {
                countries: { $set: initialState.countries },
            }),
        [updateClaimStatusFilter]: (state, payload) =>
            update(state, {
                claimStatuses: { $set: payload },
            }),
        [updateSectorFilter]: (state, payload) =>
            update(state, {
                sectors: { $set: payload },
            }),
        [updateParentCompanyFilter]: (state, payload) =>
            update(state, {
                parentCompany: { $set: payload },
            }),
        [updateFacilityTypeFilter]: (state, payload) =>
            update(state, {
                facilityType: { $set: payload },
            }),
        [updateProcessingTypeFilter]: (state, payload) =>
            update(state, {
                processingType: { $set: payload },
            }),
        [updateProductTypeFilter]: (state, payload) =>
            update(state, {
                productType: { $set: payload },
            }),
        [updateNumberofWorkersFilter]: (state, payload) =>
            update(state, {
                numberOfWorkers: { $set: payload },
            }),
        [updateNativeLanguageNameFilter]: (state, payload) =>
            update(state, {
                nativeLanguageName: { $set: payload },
            }),
        [updateCombineContributorsFilterOption]: (state, payload) =>
            update(state, {
                combineContributors: { $set: payload },
            }),
        [updateBoundaryFilter]: (state, payload) =>
            update(state, {
                boundary: { $set: payload },
            }),
        [updateSortAlgorithm]: (state, payload) =>
            update(state, {
                sortAlgorithm: { $set: payload },
            }),
        [updateListFilter]: (state, payload) =>
            update(state, {
                lists: { $set: payload },
            }),
        [updateDataSourceFilter]: (state, payload) =>
            update(state, {
                dataSources: { $set: payload },
            }),
        [updateModerationStatusFilter]: (state, payload) =>
            update(state, {
                moderationStatuses: { $set: payload },
            }),
        [resetAllFilters]: (state, isEmbedded) =>
            update(initialState, {
                contributors: {
                    $set: isEmbedded
                        ? state.contributors
                        : initialState.contributors,
                },
            }),
        [resetDrawerFilters]: state =>
            update(initialState, {
                facilityFreeTextQuery: { $set: state.facilityFreeTextQuery },
                contributors: {
                    $set: state.contributors,
                },
                countries: { $set: state.countries },
                combineContributors: { $set: state.combineContributors },
                lists: { $set: state.lists },
            }),
        [updateAllFilters]: (_state, payload) => payload,
        [completeFetchContributorOptions]: maybeSetFromQueryString(
            'contributors',
        ),
        [completeFetchContributorTypeOptions]: maybeSetFromQueryString(
            'contributorTypes',
        ),
        [completeFetchCountryOptions]: maybeSetFromQueryString('countries'),
        [completeFetchSectorOptions]: maybeSetFromQueryString('sectors'),
        [completeFetchGroupedSectorOptions]: maybeSetFromQueryString('sectors'),
        [completeFetchParentCompanyOptions]: maybeSetFromQueryString(
            'parentCompany',
        ),
        [completeSubmitLogOut]: () => initialState,
    },
    initialState,
);
