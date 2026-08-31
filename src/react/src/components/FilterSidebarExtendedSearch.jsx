import React, { forwardRef, Suspense, useEffect } from 'react';
import { bool, func, object } from 'prop-types';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';

import ShowOnly from './ShowOnly';
import StyledSelect from './Filters/StyledSelect';
import ProcessingTypeSearch from './Filters/ProcessingTypeSearch';
import {
    updateContributorTypeFilter,
    updateParentCompanyFilter,
    updateFacilityTypeFilter,
    updateProcessingTypeFilter,
    updateIsic4Filter,
    updateProductTypeFilter,
    updateNumberofWorkersFilter,
    updateNativeLanguageNameFilter,
} from '../actions/filters';

import {
    fetchContributorTypeOptions,
    fetchFacilityProcessingTypeOptions,
    fetchIsic4TaxonomyConfigIfNeeded,
    fetchNumberOfWorkersOptions,
    fetchTaxonomyCountsIfNeeded,
    fetchProcessingTypeSuggestions,
} from '../actions/filterOptions';

import {
    contributorOptionsPropType,
    contributorTypeOptionsPropType,
    facilityProcessingTypeOptionsPropType,
    facilityTypeOptionsPropType,
    processingTypeOptionsPropType,
    productTypeOptionsPropType,
    numberOfWorkerOptionsPropType,
} from '../util/propTypes';

import {
    getValueFromEvent,
    mapFacilityTypeOptions,
    restoreExactProcessingTypeLabels,
} from '../util/util';

const CONTRIBUTOR_TYPES = 'CONTRIBUTOR_TYPES';
const PARENT_COMPANY = 'PARENT_COMPANY';
const FACILITY_TYPE = 'FACILITY_TYPE';
const PROCESSING_TYPE = 'PROCESSING_TYPE';
const PRODUCT_TYPE = 'PRODUCT_TYPE';
const NUMBER_OF_WORKERS = 'NUMBER_OF_WORKERS';

const isExtendedFieldForThisContributor = (field, extendedFields) =>
    extendedFields.includes(field.toLowerCase());

const LazyIsicTaxonomySearch = React.lazy(() =>
    import('./Filters/HierarchicalTaxonomySearch/IsicTaxonomySearch'),
);

const FilterSidebarExtendedSearch = forwardRef((props, ref) => {
    const {
        contributorTypeOptions,
        facilityProcessingTypeOptions,
        processingTypeSuggestions,
        numberOfWorkersOptions,
        contributorTypes,
        updateContributorType,
        parentCompany,
        updateParentCompany,
        facilityType,
        updateFacilityType,
        processingType,
        updateProcessingType,
        isic4,
        updateIsic4,
        productType,
        updateProductType,
        numberOfWorkers,
        updateNumberOfWorkers,
        fetchingFacilities,
        fetchingExtendedOptions,
        embed,
        embedExtendedFields,
        fetchContributorTypes,
        fetchFacilityProcessingType,
        fetchSuggestionsForProcessingType,
        fetchIsic4TaxonomyConfig,
        fetchIsic4Counts,
        fetchNumberOfWorkers,
        isSideBarSearch,
        isic4Taxonomy,
        isic4Counts,
    } = props;
    const {
        config: isic4TaxonomyConfig,
        fetching: isic4TaxonomyFetching,
        error: isic4TaxonomyError,
    } = isic4Taxonomy ?? {};

    useEffect(() => {
        if (
            isic4TaxonomyConfig == null &&
            !isic4TaxonomyFetching &&
            !isic4TaxonomyError?.length
        ) {
            fetchIsic4TaxonomyConfig();
        }
    }, [
        fetchIsic4TaxonomyConfig,
        isic4TaxonomyConfig,
        isic4TaxonomyFetching,
        isic4TaxonomyError,
    ]);

    useEffect(() => {
        if (!contributorTypeOptions) {
            fetchContributorTypes();
        }
    }, [contributorTypeOptions, fetchContributorTypes]);

    useEffect(() => {
        if (!facilityProcessingTypeOptions) {
            fetchFacilityProcessingType();
        }
    }, [facilityProcessingTypeOptions, fetchFacilityProcessingType]);

    useEffect(() => {
        const restoredProcessingTypes = restoreExactProcessingTypeLabels(
            processingType,
            facilityProcessingTypeOptions,
        );
        if (restoredProcessingTypes !== processingType) {
            updateProcessingType(restoredProcessingTypes);
        }
    }, [facilityProcessingTypeOptions, processingType, updateProcessingType]);

    useEffect(() => {
        if (!numberOfWorkersOptions) {
            fetchNumberOfWorkers();
        }
    }, [numberOfWorkersOptions, fetchNumberOfWorkers]);

    if (fetchingFacilities && fetchingExtendedOptions) return null;

    if (fetchingExtendedOptions) {
        return (
            <div className="control-panel__content">
                <CircularProgress />
            </div>
        );
    }

    const isic4TaxonomyEnabled = isic4TaxonomyConfig?.enabled ?? false;
    const isic4TaxonomyConfigFailed =
        !isic4TaxonomyConfig &&
        !isic4TaxonomyFetching &&
        !!isic4TaxonomyError?.length;

    return (
        <>
            <ShowOnly when={!embed}>
                <div className="form__field">
                    <StyledSelect
                        label="Data Contributor Type"
                        id="contributorType"
                        name={CONTRIBUTOR_TYPES}
                        options={contributorTypeOptions || []}
                        value={contributorTypes}
                        onChange={updateContributorType}
                        disabled={fetchingExtendedOptions || fetchingFacilities}
                        isSideBarSearch={isSideBarSearch}
                    />
                </div>
            </ShowOnly>
            <ShowOnly
                when={
                    !embed ||
                    isExtendedFieldForThisContributor(
                        PARENT_COMPANY,
                        embedExtendedFields,
                    )
                }
            >
                <div className="form__field">
                    <StyledSelect
                        creatable
                        label="Parent Company"
                        name={PARENT_COMPANY}
                        value={parentCompany}
                        onChange={updateParentCompany}
                        placeholder="e.g. ABC Textiles Limited"
                        isSideBarSearch={isSideBarSearch}
                        aria-label="Parent company"
                        disabled={fetchingFacilities}
                    />
                </div>
            </ShowOnly>
            <ShowOnly
                when={
                    !embed ||
                    isExtendedFieldForThisContributor(
                        FACILITY_TYPE,
                        embedExtendedFields,
                    )
                }
            >
                <div className="form__field">
                    <StyledSelect
                        label="Facility Type"
                        name={FACILITY_TYPE}
                        options={mapFacilityTypeOptions(
                            facilityProcessingTypeOptions || [],
                            [],
                        )}
                        value={facilityType}
                        onChange={updateFacilityType}
                        disabled={fetchingExtendedOptions || fetchingFacilities}
                        isSideBarSearch={isSideBarSearch}
                    />
                </div>
            </ShowOnly>
            <ShowOnly
                when={
                    !embed ||
                    isExtendedFieldForThisContributor(
                        PROCESSING_TYPE,
                        embedExtendedFields,
                    )
                }
            >
                <div className="form__field">
                    <ProcessingTypeSearch
                        processingTypeSearchRef={ref}
                        label="Processing Type"
                        placeholder="Search processing types"
                        processingType={processingType}
                        onProcessingTypeChange={updateProcessingType}
                        facilityType={facilityType}
                        suggestions={processingTypeSuggestions}
                        onFetchSuggestions={fetchSuggestionsForProcessingType}
                        disabled={fetchingFacilities}
                    />
                </div>
            </ShowOnly>
            <ShowOnly when={!embed && isic4TaxonomyConfigFailed}>
                <div className="form__field">
                    <p>
                        Unable to load ISIC taxonomy settings. Try refreshing
                        the page.
                    </p>
                </div>
            </ShowOnly>
            <ShowOnly when={!embed && isic4TaxonomyEnabled}>
                <div className="form__field">
                    <Suspense fallback={null}>
                        <LazyIsicTaxonomySearch
                            counts={isic4Counts}
                            isic4={isic4}
                            onIsic4Change={updateIsic4}
                            onRequestCounts={fetchIsic4Counts}
                            disabled={fetchingFacilities}
                        />
                    </Suspense>
                </div>
            </ShowOnly>
            <ShowOnly
                when={
                    !embed ||
                    isExtendedFieldForThisContributor(
                        PRODUCT_TYPE,
                        embedExtendedFields,
                    )
                }
            >
                <div className="form__field">
                    <StyledSelect
                        creatable
                        label="Product Type"
                        name={PRODUCT_TYPE}
                        value={productType}
                        onChange={updateProductType}
                        disabled={fetchingFacilities}
                        placeholder="e.g. Jackets"
                        isSideBarSearch={isSideBarSearch}
                    />
                </div>
            </ShowOnly>
            <ShowOnly
                when={
                    !embed ||
                    isExtendedFieldForThisContributor(
                        NUMBER_OF_WORKERS,
                        embedExtendedFields,
                    )
                }
            >
                <div className="form__field">
                    <StyledSelect
                        label="Number of Workers"
                        name={NUMBER_OF_WORKERS}
                        options={numberOfWorkersOptions || []}
                        value={numberOfWorkers}
                        onChange={updateNumberOfWorkers}
                        disabled={fetchingExtendedOptions || fetchingFacilities}
                        isSideBarSearch={isSideBarSearch}
                    />
                </div>
            </ShowOnly>
        </>
    );
});

FilterSidebarExtendedSearch.defaultProps = {
    contributorTypeOptions: null,
    facilityProcessingTypeOptions: null,
    processingTypeSuggestions: Object.freeze({
        query: null,
        data: null,
        fetching: false,
        error: null,
    }),
    numberOfWorkersOptions: null,
    isic4: [],
    isic4Counts: null,
};

FilterSidebarExtendedSearch.propTypes = {
    contributorTypeOptions: contributorTypeOptionsPropType,
    facilityProcessingTypeOptions: facilityProcessingTypeOptionsPropType,
    processingTypeSuggestions: object,
    numberOfWorkersOptions: numberOfWorkerOptionsPropType,
    updateContributorType: func.isRequired,
    contributorTypes: contributorTypeOptionsPropType.isRequired,
    parentCompany: contributorOptionsPropType.isRequired,
    facilityType: facilityTypeOptionsPropType.isRequired,
    processingType: processingTypeOptionsPropType.isRequired,
    isic4: facilityTypeOptionsPropType,
    updateIsic4: func.isRequired,
    isic4Taxonomy: object.isRequired,
    isic4Counts: object,
    fetchIsic4Counts: func.isRequired,
    productType: productTypeOptionsPropType.isRequired,
    numberOfWorkers: numberOfWorkerOptionsPropType.isRequired,
    fetchingFacilities: bool.isRequired,
    fetchingExtendedOptions: bool.isRequired,
};

function mapStateToProps({
    filterOptions: {
        contributorTypes: {
            data: contributorTypeOptions,
            fetching: fetchingContributorTypes,
        },
        facilityProcessingType: {
            data: facilityProcessingTypeOptions,
            fetching: fetchingFacilityProcessingType,
        } = {},
        processingTypeSuggestions,
        numberOfWorkers: {
            data: numberOfWorkersOptions,
            fetching: fetchingNumberOfWorkers,
        },
        taxonomyCounts: { isic4: { data: isic4Counts } = {} } = {},
        isic4Taxonomy,
    },
    filters: {
        contributorTypes,
        parentCompany,
        facilityType,
        processingType,
        isic4,
        productType,
        numberOfWorkers,
        nativeLanguageName,
    },
    facilities: {
        facilities: { data: facilities, fetching: fetchingFacilities },
    },
    embeddedMap: { embed, config },
}) {
    return {
        contributorTypeOptions,
        facilityProcessingTypeOptions,
        processingTypeSuggestions,
        numberOfWorkersOptions,
        contributorTypes,
        parentCompany,
        facilityType,
        processingType,
        isic4,
        isic4Counts,
        isic4Taxonomy,
        productType,
        numberOfWorkers,
        nativeLanguageName,
        fetchingFacilities,
        facilities,
        fetchingExtendedOptions:
            fetchingContributorTypes ||
            fetchingFacilityProcessingType ||
            fetchingNumberOfWorkers,
        embed: !!embed,
        embedExtendedFields: config.extended_fields,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateContributorType: v => dispatch(updateContributorTypeFilter(v)),
        updateParentCompany: v => dispatch(updateParentCompanyFilter(v)),
        updateFacilityType: v => dispatch(updateFacilityTypeFilter(v)),
        updateProcessingType: v => dispatch(updateProcessingTypeFilter(v)),
        updateIsic4: v => dispatch(updateIsic4Filter(v)),
        updateProductType: v => dispatch(updateProductTypeFilter(v)),
        updateNumberOfWorkers: v => dispatch(updateNumberofWorkersFilter(v)),
        updateNativeLanguageName: e =>
            dispatch(updateNativeLanguageNameFilter(getValueFromEvent(e))),
        fetchContributorTypes: () => dispatch(fetchContributorTypeOptions()),
        fetchFacilityProcessingType: () =>
            dispatch(fetchFacilityProcessingTypeOptions()),
        fetchIsic4TaxonomyConfig: () =>
            dispatch(fetchIsic4TaxonomyConfigIfNeeded()),
        fetchIsic4Counts: () => dispatch(fetchTaxonomyCountsIfNeeded()),
        fetchSuggestionsForProcessingType: (query, facilityTypes) =>
            dispatch(fetchProcessingTypeSuggestions(query, facilityTypes)),
        fetchNumberOfWorkers: () => dispatch(fetchNumberOfWorkersOptions()),
    };
}

export default connect(mapStateToProps, mapDispatchToProps, null, {
    forwardRef: true,
})(FilterSidebarExtendedSearch);
