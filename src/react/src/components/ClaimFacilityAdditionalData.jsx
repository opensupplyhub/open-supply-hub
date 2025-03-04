import React, { useEffect } from 'react';
import { bool, func, string, PropTypes } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import Switch from '@material-ui/core/Switch';
import noop from 'lodash/noop';
import find from 'lodash/find';
import flow from 'lodash/flow';
import stubFalse from 'lodash/stubFalse';
import map from 'lodash/map';
import filter from 'lodash/filter';
import includes from 'lodash/includes';
import isNull from 'lodash/isNull';
import Select from 'react-select';
import Creatable from 'react-select/creatable';

import ShowOnly from './ShowOnly';
import CreatableInputOnly from './CreatableInputOnly';

import {
    updateClaimASector,
    updateClaimANumberOfWorkers,
    updateClaimALocalLanguageName,
} from '../actions/claimFacility.js';

import { fetchSectorOptions } from '../actions/filterOptions';

import { sectorOptionsPropType } from '../util/propTypes';

import { getValueFromEvent, isValidNumberOfWorkers } from '../util/util';

import {
    claimAFacilitySupportDocsFormStyles,
    claimedFacilitiesDetailsStyles,
} from '../util/styles';

import { claimAFacilityAdditionalDataFormFields } from '../util/constants';

import COLOURS from '../util/COLOURS';

const infoTitleStyle = Object.freeze({
    paddingBottom: '10px',
    color: COLOURS.NEAR_BLACK,
    fontWeight: 'bold',
});

const selectStyles = Object.freeze({
    input: provided =>
        Object.freeze({
            ...provided,
            padding: '10px',
        }),
    menu: provided =>
        Object.freeze({
            ...provided,
            zIndex: '2',
        }),
});

const {
    sectorsForm,
    sectorsDecs,
    numberOfWorkersForm,
    numberOfWorkersDesc,
    localLanguageNameForm,
    localLanguageNameDesc,
} = claimAFacilityAdditionalDataFormFields;

const InputSection = ({
    value,
    multiline,
    onChange,
    hasSwitch = false,
    switchValue = null,
    onSwitchChange = noop,
    disabled = false,
    isSelect = false,
    isMultiSelect = false,
    isCreatable = false,
    selectOptions = null,
    hasValidationErrorFn = stubFalse,
    aside = null,
    selectPlaceholder = 'Select...',
    classes,
}) => {
    let SelectComponent = null;

    const asideNode = (
        <ShowOnly when={!isNull(aside)}>
            <aside style={classes.asideStyles}>{aside}</aside>
        </ShowOnly>
    );

    if (isSelect) {
        const selectValue = (() => {
            if (!isCreatable && !isMultiSelect) {
                return find(selectOptions, ['value', value]);
            }

            if (!isCreatable && isMultiSelect) {
                return filter(selectOptions, ({ value: option }) =>
                    includes(value, option),
                );
            }

            if (isCreatable && isMultiSelect) {
                return map(value, s => ({ value: s, label: s }));
            }

            // isCreatable && !isMultiSelect creates an option object from the value
            // if it doesn't exist in the options list
            const option = find(selectOptions, ['value', value]);
            return (
                option || {
                    value,
                    label: value,
                }
            );
        })();

        if (isCreatable) {
            SelectComponent = selectOptions ? Creatable : CreatableInputOnly;
        } else {
            SelectComponent = Select;
        }

        return (
            <div style={classes.inputSectionStylesWithPadding}>
                {asideNode}
                <SelectComponent
                    onChange={onChange}
                    value={selectValue}
                    options={selectOptions}
                    disabled={disabled}
                    styles={selectStyles}
                    isMulti={isMultiSelect}
                    placeholder={selectPlaceholder}
                />
            </div>
        );
    }

    return (
        <div style={classes.inputSectionStyles}>
            <InputLabel style={classes.inputSectionLabelStyles}>
                {hasSwitch ? (
                    <span style={classes.switchSectionStyles}>
                        <Switch
                            color="primary"
                            onChange={onSwitchChange}
                            checked={switchValue}
                            style={{ zIndex: 1 }}
                        />
                        Publicly visible
                    </span>
                ) : null}
            </InputLabel>
            {asideNode}
            <TextField
                variant="outlined"
                style={classes.inputSectionFieldStyles}
                value={value}
                multiline={multiline}
                rows={6}
                onChange={onChange}
                disabled={disabled}
                error={hasValidationErrorFn()}
            />
        </div>
    );
};

function ClaimFacilityAdditionalData({
    sectors,
    updateSectors,
    numberOfWorkers,
    updateNumberOfWorkers,
    localLanguageName,
    updateLocalLanguageName,
    sectorOptions,
    fetchSectors,
    fetching,
}) {
    useEffect(() => {
        if (!sectorOptions) {
            fetchSectors();
        }
    }, [sectorOptions, fetchSectors]);

    return (
        <>
            <div style={claimAFacilitySupportDocsFormStyles.inputGroupStyles}>
                <InputLabel htmlFor={sectorsForm.id}>
                    <Typography variant="display1" style={infoTitleStyle}>
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
                />
            </div>
            <div style={claimAFacilitySupportDocsFormStyles.inputGroupStyles}>
                <InputLabel htmlFor={numberOfWorkersForm.id}>
                    <Typography variant="display1" style={infoTitleStyle}>
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
                    style={claimAFacilitySupportDocsFormStyles.textFieldStyles}
                    value={numberOfWorkers}
                    placeholder={numberOfWorkersForm.placeholder}
                    onChange={updateNumberOfWorkers}
                    disabled={fetching}
                />
            </div>
            <div style={claimAFacilitySupportDocsFormStyles.inputGroupStyles}>
                <InputLabel htmlFor={localLanguageNameForm.id}>
                    <Typography variant="display1" style={infoTitleStyle}>
                        {localLanguageNameForm.label}
                    </Typography>
                </InputLabel>
                <Typography variant="subheading">
                    {localLanguageNameDesc.label}
                </Typography>
                <TextField
                    id={localLanguageNameForm.id}
                    variant="outlined"
                    style={claimAFacilitySupportDocsFormStyles.textFieldStyles}
                    value={localLanguageName}
                    placeholder={localLanguageNameForm.placeholder}
                    onChange={updateLocalLanguageName}
                    disabled={fetching}
                />
            </div>
        </>
    );
}

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
)(withStyles(claimedFacilitiesDetailsStyles)(ClaimFacilityAdditionalData));
