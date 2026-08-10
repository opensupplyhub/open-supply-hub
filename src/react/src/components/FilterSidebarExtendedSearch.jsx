import React, { Suspense, useEffect } from 'react';
import { bool, func, object } from 'prop-types';
import { connect } from 'react-redux';
import CircularProgress from '@material-ui/core/CircularProgress';

import ShowOnly from './ShowOnly';
import StyledSelect from './Filters/StyledSelect';
import HierarchicalTaxonomySearch, {
    TAXONOMY_KINDS,
} from './Filters/HierarchicalTaxonomySearch';

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
    fetchNumberOfWorkersOptions,
    fetchTaxonomyCountsIfNeeded,
} from '../actions/filterOptions';

import {
    contributorOptionsPropType,
    contributorTypeOptionsPropType,
    facilityTypeOptionsPropType,
    processingTypeOptionsPropType,
    facilityProcessingTypeOptionsPropType,
    productTypeOptionsPropType,
    numberOfWorkerOptionsPropType,
} from '../util/propTypes';

import {
    getValueFromEvent,
    mapProcessingTypeOptions,
    mapFacilityTypeOptions,
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

function FilterSidebarExtendedSearch({
    contributorTypeOptions,
    facilityProcessingTypeOptions,
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
    fetchTaxonomyCountsForKind,
    fetchNumberOfWorkers,
    isSideBarSearch,
}) {
    useEffect(() => {
        if (!contributorTypeOptions) {
            fetchContributorTypes();
        }
    }, [contributorTypeOptions, fetchContributorTypes]);

    useEffect(() => {
        if (embed && !facilityProcessingTypeOptions) {
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
            <ShowOnly when={!embed}>
                <div className="form__field">
                    <HierarchicalTaxonomySearch
                        label="Facility type & processing type"
                        placeholder="Search facility or processing type"
                        counts={taxonomyCounts.facility_processing}
                        facilityType={facilityType}
                        processingType={processingType}
                        onFacilityTypeChange={updateFacilityType}
                        onProcessingTypeChange={updateProcessingType}
                        onRequestCounts={() =>
                            fetchTaxonomyCountsForKind(
                                TAXONOMY_KINDS.FACILITY_PROCESSING,
                            )
                        }
                        disabled={fetchingFacilities}
                    />
                </div>
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
                            processingType,
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
                    <StyledSelect
                        label="Processing Type"
                        name={PROCESSING_TYPE}
                        options={mapProcessingTypeOptions(
                            facilityProcessingTypeOptions || [],
                            facilityType,
                        )}
                        value={processingType}
                        onChange={updateProcessingType}
                        disabled={fetchingExtendedOptions || fetchingFacilities}
                        isSideBarSearch={isSideBarSearch}
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
}

FilterSidebarExtendedSearch.defaultProps = {
    contributorTypeOptions: null,
    facilityProcessingTypeOptions: null,
    taxonomyCounts: Object.freeze({
        facility_processing: null,
        isic4: null,
    }),
    numberOfWorkersOptions: null,
};

FilterSidebarExtendedSearch.propTypes = {
    contributorTypeOptions: contributorTypeOptionsPropType,
    facilityProcessingTypeOptions: facilityProcessingTypeOptionsPropType,
    taxonomyCounts: object,
    numberOfWorkersOptions: numberOfWorkerOptionsPropType,
    updateContributorType: func.isRequired,
    contributorTypes: contributorTypeOptionsPropType.isRequired,
    parentCompany: contributorOptionsPropType.isRequired,
    facilityType: facilityTypeOptionsPropType.isRequired,
    processingType: processingTypeOptionsPropType.isRequired,
    isic4: facilityTypeOptionsPropType,
    updateIsic4: func.isRequired,
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
        },
        taxonomyCounts: {
            facility_processing: { data: facilityProcessingCounts } = {},
            isic4: { data: isic4Counts } = {},
        } = {},
        numberOfWorkers: {
            data: numberOfWorkersOptions,
            fetching: fetchingNumberOfWorkers,
        },
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
        taxonomyCounts: {
            facility_processing: facilityProcessingCounts,
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
        fetchTaxonomyCountsForKind: kind =>
            dispatch(fetchTaxonomyCountsIfNeeded({ kinds: [kind] })),
        fetchNumberOfWorkers: () => dispatch(fetchNumberOfWorkersOptions()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(FilterSidebarExtendedSearch);
