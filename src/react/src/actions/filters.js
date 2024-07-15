import update from 'immutability-helper';
import { createAction } from 'redux-act';

import {
    createFiltersFromQueryString,
    updateListWithLabels,
} from '../util/util';
import { optionsForSortingResults } from '../util/constants';

import { setEmbeddedMapStatusFromQueryString } from '../actions/embeddedMap';

export const updateFacilityFreeTextQueryFilter = createAction(
    'UPDATE_FACILITY_FREE_TEXT_QUERY_FILTER',
);
export const updateContributorFilter = createAction(
    'UPDATE_CONTRIBUTOR_FILTER',
);
export const updateContributorTypeFilter = createAction(
    'UPDATE_CONTRIBUTOR_TYPE_FILTER',
);
export const updateListFilter = createAction('UPDATE_LIST_FILTER');
export const updateCountryFilter = createAction('UPDATE_COUNTRY_FILTER');
export const updateSectorFilter = createAction('UPDATE_SECTOR_FILTER');
export const updateParentCompanyFilter = createAction(
    'UPDATE_PARENT_COMPANY_FILTER',
);
export const updateFacilityTypeFilter = createAction(
    'UPDATE_FACILITY_TYPE_FILTER',
);
export const updateProcessingTypeFilter = createAction(
    'UPDATE_PROCESSING_TYPE_FILTER',
);
export const updateProductTypeFilter = createAction(
    'UPDATE_PRODUCT_TYPE_FILTER',
);
export const updateNumberofWorkersFilter = createAction(
    'UPDATE_NUMBER_OF_WORKERS_FILTER',
);
export const updateNativeLanguageNameFilter = createAction(
    'UPDATE_NATIVE_LANGUAGE_NAME_FILTER',
);
export const updateCombineContributorsFilterOption = createAction(
    'UPDATE_COMBINE_CONTRIBUTORS_FILTER_OPTION',
);
export const updateBoundaryFilter = createAction('UPDATE_BOUNDARY_FILTER');
export const updateSortAlgorithm = createAction('UPDATE_SORT_ALGORITHM');
export const resetAllFilters = createAction('RESET_ALL_FILTERS');
export const updateAllFilters = createAction('UPDATE_ALL_FILTERS');
export const resetDrawerFilters = createAction('RESET_DRAWER_FILTERS');

export function setFiltersFromQueryString(qs = '') {
    return (dispatch, getState) => {
        if (!qs) {
            return null;
        }

        dispatch(setEmbeddedMapStatusFromQueryString(qs));

        // If contributor / parent company data already exists in the state,
        // use it to match filters from the query string with labels.
        // Otherwise, use the query string values directly. It will be updated
        // later when the contributor data is loaded.

        const filters = createFiltersFromQueryString(qs);
        const {
            filterOptions: {
                contributors: { data: contributors },
                parentCompanies: { data: parentCompanies },
                lists: { data: lists },
            },
            embeddedMap: { embed },
        } = getState();

        let payload = contributors
            ? update(filters, {
                  contributors: {
                      $set: updateListWithLabels(
                          filters.contributors,
                          contributors,
                      ),
                  },
              })
            : filters;

        payload = parentCompanies
            ? update(payload, {
                  parentCompany: {
                      $set: updateListWithLabels(
                          filters.parentCompany,
                          parentCompanies,
                      ),
                  },
              })
            : payload;

        payload = lists
            ? update(payload, {
                  lists: {
                      $set: updateListWithLabels(filters.lists, lists),
                  },
              })
            : payload;

        payload = embed
            ? update(payload, {
                  sortAlgorithm: {
                      $set: optionsForSortingResults[0],
                  },
              })
            : payload;

        return dispatch(updateAllFilters(payload));
    };
}
