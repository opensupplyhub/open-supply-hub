import React, { useEffect } from 'react';
import { bool, func, string, PropTypes, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import flow from 'lodash/flow';
import map from 'lodash/map';

import {
    updateClaimASector,
    updateClaimANumberOfWorkers,
    updateClaimALocalLanguageName,
} from '../actions/claimFacility.js';

import { fetchSectorOptions } from '../actions/filterOptions';

import { sectorOptionsPropType } from '../util/propTypes';

import {
    getValueFromEvent,
    isValidNumberOfWorkers,
    getNumberOfWorkersValidationError,
} from '../util/util';

import {
    claimedFacilitiesDetailsStyles,
    textFieldErrorStyles,
} from '../util/styles';

import { claimAFacilityAdditionalDataFormFields } from '../util/constants';
import InputSection from '../components/InputSection';
import InputErrorText from '../components/Contribute/InputErrorText';
import FreeEmissionsEstimate from '../components/FreeEmissionsEstimate';

const {
    sectorsForm,
    sectorsDecs,
    numberOfWorkersForm,
    numberOfWorkersDesc,
    localLanguageNameForm,
    localLanguageNameDesc,
} = claimAFacilityAdditionalDataFormFields;

const mergedStyles = {
    ...textFieldErrorStyles(),
    ...claimedFacilitiesDetailsStyles(),
};

const ClaimFacilityAdditionalData = ({
    sectors,
    updateSectors,
    numberOfWorkers,
    updateNumberOfWorkers,
    localLanguageName,
    updateLocalLanguageName,
    sectorOptions,
    fetchSectors,
    fetching,
    classes,
}) => {
    useEffect(() => {
        if (!sectorOptions) {
            fetchSectors();
        }
    }, [sectorOptions, fetchSectors]);

    return (
        <>
            <div className={classes.inputGroupStyles}>
                <InputLabel htmlFor={sectorsForm.id}>
                    <Typography
                        variant="title"
                        className={classes.boldTitleStyle}
                    >
                        {sectorsForm.label}
                    </Typography>
                </InputLabel>
                <Typography variant="subheading">
                    {sectorsDecs.label}
                </Typography>
                <InputSection
                    value={sectors}
                    onChange={updateSectors}
                    disabled={fetching}
                    isSelect
                    isMultiSelect
                    selectOptions={sectorOptions || []}
                    selectPlaceholder={sectorsForm.placeholder}
                    isClaimFacilityAdditionalDataPage
                />
            </div>
            <div className={classes.inputGroupStyles}>
                <InputLabel htmlFor={numberOfWorkersForm.id}>
                    <Typography
                        variant="title"
                        className={classes.boldTitleStyle}
                    >
                        {numberOfWorkersForm.label}
                    </Typography>
                </InputLabel>
                <Typography variant="subheading">
                    {numberOfWorkersDesc.label}
                </Typography>
                <TextField
                    id={numberOfWorkersForm.id}
                    error={!isValidNumberOfWorkers(numberOfWorkers)}
                    variant="outlined"
                    className={classes.textFieldStyles}
                    value={numberOfWorkers}
                    placeholder={numberOfWorkersForm.placeholder}
                    onChange={updateNumberOfWorkers}
                    disabled={fetching}
                    helperText={
                        !isValidNumberOfWorkers(numberOfWorkers) && (
                            <InputErrorText
                                text={getNumberOfWorkersValidationError(
                                    numberOfWorkers,
                                )}
                            />
                        )
                    }
                    FormHelperTextProps={{
                        className: classes.helperText,
                    }}
                    InputProps={{
                        classes: {
                            input: `
                                ${
                                    !isValidNumberOfWorkers(numberOfWorkers) &&
                                    classes.errorStyle
                                }`,
                        },
                    }}
                />
            </div>
            <div className={classes.inputGroupStyles}>
                <InputLabel htmlFor={localLanguageNameForm.id}>
                    <Typography
                        variant="title"
                        className={classes.boldTitleStyle}
                    >
                        {localLanguageNameForm.label}
                    </Typography>
                </InputLabel>
                <Typography variant="subheading">
                    {localLanguageNameDesc.label}
                </Typography>
                <TextField
                    id={localLanguageNameForm.id}
                    variant="outlined"
                    className={classes.textFieldStyles}
                    value={localLanguageName}
                    placeholder={localLanguageNameForm.placeholder}
                    onChange={updateLocalLanguageName}
                    disabled={fetching}
                />
            </div>
            <FreeEmissionsEstimate />
        </>
    );
};

ClaimFacilityAdditionalData.defaultProps = {
    sectors: [],
    sectorOptions: null,
};

ClaimFacilityAdditionalData.propTypes = {
    sectors: PropTypes.arrayOf(PropTypes.string),
    numberOfWorkers: string.isRequired,
    updateNumberOfWorkers: func.isRequired,
    localLanguageName: string.isRequired,
    updateLocalLanguageName: func.isRequired,
    sectorOptions: sectorOptionsPropType,
    fetchSectors: func.isRequired,
    fetching: bool.isRequired,
    classes: object.isRequired,
};

function mapStateToProps({
    claimFacility: {
        claimData: {
            formData: { sectors, numberOfWorkers, localLanguageName },
            fetching,
        },
    },
    filterOptions: {
        sectors: { data: sectorOptions, fetching: fetchingSectors },
    },
}) {
    return {
        sectors,
        numberOfWorkers,
        localLanguageName,
        sectorOptions,
        fetching: fetching || fetchingSectors,
    };
}

function mapDispatchToProps(dispatch) {
    const makeDispatchMultiSelectFn = updateFn =>
        flow(selection => map(selection, 'value'), updateFn, dispatch);
    return {
        updateSectors: makeDispatchMultiSelectFn(updateClaimASector),
        updateNumberOfWorkers: e =>
            dispatch(updateClaimANumberOfWorkers(getValueFromEvent(e))),
        updateLocalLanguageName: e =>
            dispatch(updateClaimALocalLanguageName(getValueFromEvent(e))),
        fetchSectors: () => dispatch(fetchSectorOptions()),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(mergedStyles)(ClaimFacilityAdditionalData));
