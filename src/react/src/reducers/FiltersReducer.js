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
    updateIsic4Filter,
    updateProductTypeFilter,
    updateNumberofWorkersFilter,
    updateNativeLanguageNameFilter,
    updateSortAlgorithm,
    updateCombineContributorsFilterOption,
    updateCombineFacilityProcessingIsicFilterOption,
    updateBoundaryFilter,
    resetAllFilters,
    resetDrawerFilters,
    updateAllFilters,
    updateDataSourceFilter,
    updateModerationStatusFilter,
    setPartnerContributorFilter,
} from '../actions/filters';

import {
    completeFetchContributorOptions,
    completeFetchContributorTypeOptions,
    completeFetchCountryOptions,
    completeFetchSectorOptions,
    completeFetchParentCompanyOptions,
    completeFetchGroupedSectorOptions,
} from '../actions/filterOptions';
import { completeFetchPartnerGroupContributors } from '../actions/partnerGroupContributors';

import { completeSubmitLogOut } from '../actions/auth';

import {
    mapPartnerGroupContributorsToSelectOptions,
    updateListWithLabels,
} from '../util/util';

const shouldCombineFacilityProcessingIsic = ({
    facilityType,
    processingType,
    isic4,
}) =>
    ((facilityType && facilityType.length > 0) ||
        (processingType && processingType.length > 0)) &&
    isic4 &&
    isic4.length > 0;

const maybeClearCombineFacilityProcessingIsic = state =>
    shouldCombineFacilityProcessingIsic(state)
        ? state
        : update(state, {
              combineFacilityProcessingIsic: { $set: '' },
          });

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
    isic4: Object.freeze([]),
    productType: Object.freeze([]),
    numberOfWorkers: Object.freeze([]),
    dataSources: Object.freeze([]),
    moderationStatuses: Object.freeze([]),
    nativeLanguageName: '',
    combineContributors: '',
    combineFacilityProcessingIsic: '',
    boundary: null,
    lists: Object.freeze([]),
    partnerContributors: Object.freeze([]),
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
            maybeClearCombineFacilityProcessingIsic(
                update(state, {
                    facilityType: { $set: payload },
                }),
            ),
        [updateProcessingTypeFilter]: (state, payload) =>
            maybeClearCombineFacilityProcessingIsic(
                update(state, {
                    processingType: { $set: payload },
                }),
            ),
        [updateIsic4Filter]: (state, payload) =>
            maybeClearCombineFacilityProcessingIsic(
                update(state, {
                    isic4: { $set: payload },
                }),
            ),
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
        [updateCombineFacilityProcessingIsicFilterOption]: (state, payload) =>
            update(state, {
                combineFacilityProcessingIsic: { $set: payload },
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
        [setPartnerContributorFilter]: (state, payload) =>
            update(state, {
                partnerContributors: { $set: payload },
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
                combineFacilityProcessingIsic: {
                    $set: state.combineFacilityProcessingIsic,
                },
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
        [completeFetchPartnerGroupContributors]: (state, payload) =>
            update(state, {
                partnerContributors: {
                    $set: updateListWithLabels(
                        state.partnerContributors,
                        mapPartnerGroupContributorsToSelectOptions(
                            payload?.results || [],
                        ),
                    ),
                },
            }),
        [completeSubmitLogOut]: () => initialState,
    },
    initialState,
);
