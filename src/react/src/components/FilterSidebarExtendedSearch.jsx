import React, { Suspense, forwardRef, useEffect } from 'react';
import { bool, func, object, string } from 'prop-types';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';
import Checkbox from '@material-ui/core/Checkbox';
import FormControlLabel from '@material-ui/core/FormControlLabel';

import ShowOnly from './ShowOnly';
import StyledSelect from './Filters/StyledSelect';
import ProcessingTypeSearch from './Filters/ProcessingTypeSearch';
import { TAXONOMY_KINDS } from './Filters/HierarchicalTaxonomySearch/utils';
import {
    updateContributorTypeFilter,
    updateParentCompanyFilter,
    updateFacilityTypeFilter,
    updateProcessingTypeFilter,
    updateIsic4Filter,
    updateProductTypeFilter,
    updateNumberofWorkersFilter,
    updateNativeLanguageNameFilter,
    updateCombineFacilityProcessingIsicFilterOption,
} from '../actions/filters';

import {
    fetchContributorTypeOptions,
    fetchFacilityProcessingTypeOptions,
    fetchIsic4TaxonomyConfigIfNeeded,
    fetchNumberOfWorkersOptions,
    fetchProcessingTypeSuggestions,
    fetchTaxonomyCountsIfNeeded,
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

import { getValueFromEvent, mapFacilityTypeOptions } from '../util/util';

const CONTRIBUTOR_TYPES = 'CONTRIBUTOR_TYPES';
const PARENT_COMPANY = 'PARENT_COMPANY';
const FACILITY_TYPE = 'FACILITY_TYPE';
const PROCESSING_TYPE = 'PROCESSING_TYPE';
const PRODUCT_TYPE = 'PRODUCT_TYPE';
const NUMBER_OF_WORKERS = 'NUMBER_OF_WORKERS';

const isExtendedFieldForThisContributor = (field, extendedFields) =>
    extendedFields.includes(field.toLowerCase());

const hasFacilityProcessingSelections = (facilityType, processingType) =>
    (facilityType && facilityType.length > 0) ||
    (processingType && processingType.length > 0);

const shouldShowCombineFacilityProcessingIsic = (
    facilityType,
    processingType,
    isic4,
) =>
    hasFacilityProcessingSelections(facilityType, processingType) &&
    isic4 &&
    isic4.length > 0;

const LazyIsicTaxonomySearch = React.lazy(() =>
    import('./Filters/HierarchicalTaxonomySearch/IsicTaxonomySearch'),
);

const FilterSidebarExtendedSearch = forwardRef((props, ref) => {
    const {
        contributorTypeOptions,
        facilityProcessingTypeOptions,
        processingTypeSuggestions,
        taxonomyCounts,
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
        combineFacilityProcessingIsic,
        updateCombineFacilityProcessingIsic,
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
        fetchIsic4TaxonomyConfig,
        fetchSuggestionsForProcessingType,
        fetchTaxonomyCountsForKind,
        fetchNumberOfWorkers,
        isSideBarSearch,
        isic4Taxonomy,
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
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isic4TaxonomyConfig, isic4TaxonomyFetching, isic4TaxonomyError]);

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
    const showCombineFacilityProcessingIsic =
        isic4TaxonomyEnabled &&
        shouldShowCombineFacilityProcessingIsic(
            facilityType,
            processingType,
            isic4,
        );

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
                            counts={taxonomyCounts.isic4}
                            isic4={isic4}
                            onIsic4Change={updateIsic4}
                            onRequestCounts={() =>
                                fetchTaxonomyCountsForKind(TAXONOMY_KINDS.ISIC4)
                            }
                            disabled={fetchingFacilities}
                        />
                    </Suspense>
                </div>
            </ShowOnly>
            <ShowOnly when={showCombineFacilityProcessingIsic}>
                <div className="form__field" style={{ marginTop: '-8px' }}>
                    <FormControlLabel
                        control={
                            <Checkbox
                                checked={!!combineFacilityProcessingIsic}
                                onChange={updateCombineFacilityProcessingIsic}
                                color="primary"
                                value={combineFacilityProcessingIsic}
                                disabled={fetchingFacilities}
                            />
                        }
                        label="Match both facility type and ISIC categories"
                    />
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
    taxonomyCounts: Object.freeze({
        isic4: null,
    }),
    numberOfWorkersOptions: null,
    isic4: [],
    combineFacilityProcessingIsic: '',
};

FilterSidebarExtendedSearch.propTypes = {
    contributorTypeOptions: contributorTypeOptionsPropType,
    facilityProcessingTypeOptions: facilityProcessingTypeOptionsPropType,
    processingTypeSuggestions: object,
    taxonomyCounts: object,
    numberOfWorkersOptions: numberOfWorkerOptionsPropType,
    updateContributorType: func.isRequired,
    contributorTypes: contributorTypeOptionsPropType.isRequired,
    parentCompany: contributorOptionsPropType.isRequired,
    facilityType: facilityTypeOptionsPropType.isRequired,
    processingType: processingTypeOptionsPropType.isRequired,
    isic4: facilityTypeOptionsPropType,
    updateIsic4: func.isRequired,
    combineFacilityProcessingIsic: string,
    updateCombineFacilityProcessingIsic: func.isRequired,
    productType: productTypeOptionsPropType.isRequired,
    numberOfWorkers: numberOfWorkerOptionsPropType.isRequired,
    fetchingFacilities: bool.isRequired,
    fetchingExtendedOptions: bool.isRequired,
    fetchTaxonomyCountsForKind: func.isRequired,
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
        taxonomyCounts: { isic4: { data: isic4Counts } = {} } = {},
        numberOfWorkers: {
            data: numberOfWorkersOptions,
            fetching: fetchingNumberOfWorkers,
        },
        isic4Taxonomy: {
            config: isic4TaxonomyConfig,
            fetching: isic4TaxonomyFetching,
            error: isic4TaxonomyError,
            data: isic4TaxonomyData,
        } = {},
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
        combineFacilityProcessingIsic,
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
        taxonomyCounts: {
            isic4: isic4Counts,
        },
        numberOfWorkersOptions,
        contributorTypes,
        parentCompany,
        facilityType,
        processingType,
        isic4,
        productType,
        numberOfWorkers,
        nativeLanguageName,
        combineFacilityProcessingIsic,
        fetchingFacilities,
        facilities,
        fetchingExtendedOptions:
            fetchingContributorTypes ||
            fetchingFacilityProcessingType ||
            fetchingNumberOfWorkers,
        embed: !!embed,
        embedExtendedFields: config.extended_fields,
        isic4Taxonomy: {
            config: isic4TaxonomyConfig,
            fetching: isic4TaxonomyFetching,
            error: isic4TaxonomyError,
            data: isic4TaxonomyData,
        },
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateContributorType: v => dispatch(updateContributorTypeFilter(v)),
        updateParentCompany: v => dispatch(updateParentCompanyFilter(v)),
        updateFacilityType: v => dispatch(updateFacilityTypeFilter(v)),
        updateProcessingType: v => dispatch(updateProcessingTypeFilter(v)),
        updateIsic4: v => dispatch(updateIsic4Filter(v)),
        updateCombineFacilityProcessingIsic: e =>
            dispatch(
                updateCombineFacilityProcessingIsicFilterOption(
                    e.target.checked ? 'AND' : '',
                ),
            ),
        updateProductType: v => dispatch(updateProductTypeFilter(v)),
        updateNumberOfWorkers: v => dispatch(updateNumberofWorkersFilter(v)),
        updateNativeLanguageName: e =>
            dispatch(updateNativeLanguageNameFilter(getValueFromEvent(e))),
        fetchContributorTypes: () => dispatch(fetchContributorTypeOptions()),
        fetchFacilityProcessingType: () =>
            dispatch(fetchFacilityProcessingTypeOptions()),
        fetchIsic4TaxonomyConfig: () =>
            dispatch(fetchIsic4TaxonomyConfigIfNeeded()),
        fetchSuggestionsForProcessingType: (query, facilityTypes) =>
            dispatch(fetchProcessingTypeSuggestions(query, facilityTypes)),
        fetchTaxonomyCountsForKind: kind =>
            dispatch(fetchTaxonomyCountsIfNeeded({ kinds: [kind] })),
        fetchNumberOfWorkers: () => dispatch(fetchNumberOfWorkersOptions()),
    };
}

export default connect(mapStateToProps, mapDispatchToProps, null, {
    forwardRef: true,
})(FilterSidebarExtendedSearch);
