import React, { useEffect } from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core';

import {
    clearMergeTargetFacility,
    updateMergeTargetFacilityOSID,
    fetchMergeTargetFacility,
    clearFacilityToMerge,
    updateFacilityToMergeOSID,
    fetchFacilityToMerge,
    resetMergeFacilitiesState,
    mergeFacilities,
    flipFacilitiesToMerge,
    clearMergeFacilitiesError,
} from '../actions/mergeFacilities';

import {
    getValueFromEvent,
    makeSubmitFormOnEnterKeyPressFunction,
} from '../util/util';

import { facilityDetailsPropType } from '../util/propTypes';

import DashboardFacilityCard from './DashboardFacilityCard';
import DashboardMergeFacilityControls from './DashboardMergeFacilityControls';

const dashboardMergeFacilitiesStyles = () =>
    Object.freeze({
        dashboardFacilityCardsContainer: {
            width: '100%',
            display: 'flex',
            justifyContent: 'space-between',
        },
    });

function DashboardMergeFacilities({
    isModalMode,
    targetOSID,
    targetData,
    targetFetching,
    targetError,
    toMergeOSID,
    toMergeData,
    toMergeFetching,
    toMergeError,
    updateTargetOSID,
    clearTargetFacility,
    fetchTargetFacility,
    fetchTargetFacilityOnEnterKeyPress,
    updateToMergeOSID,
    clearToMergeFacility,
    fetchToMergeFacility,
    fetchToMergeFacilityOnEnterKeyPress,
    resetMergeState,
    mergeSelectedFacilities,
    merging,
    errorMerging,
    flipSelectedFacilities,
    classes,
    handleClearMergeFacilitiesError,
}) {
    useEffect(() => (!isModalMode ? resetMergeState : undefined), [
        isModalMode,
        resetMergeState,
    ]);

    return (
        <>
            <DashboardMergeFacilityControls
                handleMerge={mergeSelectedFacilities}
                handleFlip={flipSelectedFacilities}
                merging={merging}
                error={errorMerging}
                disabled={
                    targetFetching ||
                    toMergeFetching ||
                    !targetData ||
                    !toMergeData
                }
                toMergeData={toMergeData}
                targetData={targetData}
                handleClearFacilityToMerge={handleClearMergeFacilitiesError}
            />
            <div className={classes.dashboardFacilityCardsContainer}>
                <DashboardFacilityCard
                    updateOSID={updateTargetOSID}
                    fetchFacility={fetchTargetFacility}
                    clearFacility={clearTargetFacility}
                    osID={targetOSID}
                    data={targetData}
                    fetching={targetFetching}
                    error={targetError}
                    handleEnterKeyPress={fetchTargetFacilityOnEnterKeyPress}
                    title="Target facility for merge"
                />
                <DashboardFacilityCard
                    updateOSID={updateToMergeOSID}
                    fetchFacility={fetchToMergeFacility}
                    clearFacility={clearToMergeFacility}
                    osID={toMergeOSID}
                    data={toMergeData}
                    fetching={toMergeFetching}
                    error={toMergeError}
                    handleEnterKeyPress={fetchToMergeFacilityOnEnterKeyPress}
                    title="Facility to merge into target"
                />
            </div>
        </>
    );
}

DashboardMergeFacilities.defaultProps = {
    isModalMode: false,
    targetData: null,
    targetError: null,
    toMergeData: null,
    toMergeError: null,
    errorMerging: null,
};

DashboardMergeFacilities.propTypes = {
    isModalMode: bool,
    targetOSID: string.isRequired,
    targetData: facilityDetailsPropType,
    targetFetching: bool.isRequired,
    targetError: arrayOf(string),
    toMergeOSID: string.isRequired,
    toMergeData: facilityDetailsPropType,
    toMergeFetching: bool.isRequired,
    toMergeError: arrayOf(string),
    updateTargetOSID: func.isRequired,
    clearTargetFacility: func.isRequired,
    fetchTargetFacility: func.isRequired,
    fetchTargetFacilityOnEnterKeyPress: func.isRequired,
    updateToMergeOSID: func.isRequired,
    clearToMergeFacility: func.isRequired,
    fetchToMergeFacility: func.isRequired,
    fetchToMergeFacilityOnEnterKeyPress: func.isRequired,
    resetMergeState: func.isRequired,
    mergeSelectedFacilities: func.isRequired,
    merging: bool.isRequired,
    errorMerging: arrayOf(string),
    flipSelectedFacilities: func.isRequired,
};

function mapStateToProps({
    mergeFacilities: {
        targetFacility: {
            osID: targetOSID,
            data: targetData,
            fetching: targetFetching,
            error: targetError,
        },
        facilityToMerge: {
            osID: toMergeOSID,
            data: toMergeData,
            fetching: toMergeFetching,
            error: toMergeError,
        },
        merge: { fetching: merging, error: errorMerging },
    },
}) {
    return {
        targetOSID,
        targetData,
        targetFetching,
        targetError,
        toMergeOSID,
        toMergeData,
        toMergeFetching,
        toMergeError,
        merging,
        errorMerging,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        updateTargetOSID: e =>
            dispatch(updateMergeTargetFacilityOSID(getValueFromEvent(e))),
        clearTargetFacility: () => dispatch(clearMergeTargetFacility()),
        fetchTargetFacility: () => dispatch(fetchMergeTargetFacility()),
        fetchTargetFacilityOnEnterKeyPress: makeSubmitFormOnEnterKeyPressFunction(
            () => dispatch(fetchMergeTargetFacility()),
        ),
        updateToMergeOSID: e =>
            dispatch(updateFacilityToMergeOSID(getValueFromEvent(e))),
        clearToMergeFacility: () => dispatch(clearFacilityToMerge()),
        fetchToMergeFacility: () => dispatch(fetchFacilityToMerge()),
        fetchToMergeFacilityOnEnterKeyPress: makeSubmitFormOnEnterKeyPressFunction(
            () => dispatch(fetchFacilityToMerge()),
        ),
        resetMergeState: () => dispatch(resetMergeFacilitiesState()),
        mergeSelectedFacilities: () => dispatch(mergeFacilities()),
        flipSelectedFacilities: () => dispatch(flipFacilitiesToMerge()),
        handleClearMergeFacilitiesError: () =>
            dispatch(clearMergeFacilitiesError()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(dashboardMergeFacilitiesStyles)(DashboardMergeFacilities));
