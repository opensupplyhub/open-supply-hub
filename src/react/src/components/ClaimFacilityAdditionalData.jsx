import React, { useEffect } from 'react';
import { bool, func, string } from 'prop-types';
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

import { getValueFromEvent } from '../util/util';

import { claimAFacilitySupportDocsFormStyles } from '../util/styles';

import { claimAFacilityAdditionalDataFormFields } from '../util/constants';

import COLOURS from '../util/COLOURS';

const yourContactInfoTitleStyle = Object.freeze({
    paddingBottom: '10px',
    color: COLOURS.NEAR_BLACK,
    fontWeight: 'bold',
});

const yourContactInfoDescStyle = Object.freeze({
    fontWeight: 'bold',
});

const claimedFacilitiesDetailsStyles = Object.freeze({
    containerStyles: Object.freeze({
        display: 'flex',
        width: '100%',
        justifyContent: 'space-between',
        marginBottom: '100px',
        padding: '10px 0 10px',
    }),
    formStyles: Object.freeze({
        width: '60%',
    }),
    headingStyles: Object.freeze({
        padding: '10px 0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    }),
    inputSectionStyles: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        width: '95%',
        padding: '10px 0 10px',
    }),
    inputSectionLabelStyles: Object.freeze({
        fontSize: '18px',
        fontWeight: '400',
        padding: '10px 0',
        color: '#000',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    }),
    inputSectionFieldStyles: Object.freeze({
        width: '100%',
    }),
    switchSectionStyles: Object.freeze({
        fontSize: '15px',
        fontWeight: '400',
        display: 'flex',
        alignItems: 'center',
        color: COLOURS.DARK_GREY,
    }),
    controlStyles: Object.freeze({
        width: '100%',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '10px 0',
    }),
    errorStyles: Object.freeze({
        width: '100%',
        padding: '10px 0',
        color: 'red',
    }),
    asideStyles: Object.freeze({
        padding: '5px 20px 20px 0',
    }),
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
    sectors,
    sectorsDecs,
    numberOfWorkers,
    numberOfWorkersDesc,
    localLanguageName,
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
}) => {
    let SelectComponent = null;

    const asideNode = (
        <ShowOnly when={!isNull(aside)}>
            <aside style={claimedFacilitiesDetailsStyles.asideStyles}>
                {aside}
            </aside>
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
            <div style={claimedFacilitiesDetailsStyles.inputSectionStyles}>
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
        <div style={claimedFacilitiesDetailsStyles.inputSectionStyles}>
            <InputLabel
                style={claimedFacilitiesDetailsStyles.inputSectionLabelStyles}
            >
                {hasSwitch ? (
                    <span
                        style={
                            claimedFacilitiesDetailsStyles.switchSectionStyles
                        }
                    >
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
                style={claimedFacilitiesDetailsStyles.inputSectionFieldStyles}
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
    sectorsValue,
    updateSectors,
    numberOfWorkersValue,
    updateNumberOfWorkers,
    localLanguageNameValue,
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
            <div>
                <Typography
                    variant="display3"
                    style={yourContactInfoTitleStyle}
                >
                    Additional Data
                </Typography>
                <Typography variant="heading" style={yourContactInfoDescStyle}>
                    Use the form below to upload additional information about
                    this production location.
                </Typography>
            </div>
            <div style={claimAFacilitySupportDocsFormStyles.inputGroupStyles}>
                <InputLabel htmlFor={sectors.id}>
                    <Typography
                        variant="display1"
                        style={yourContactInfoTitleStyle}
                    >
                        {sectors.label}
                    </Typography>
                </InputLabel>
                <Typography variant="subheading">
                    {sectorsDecs.label}
                </Typography>
                <InputSection
                    value={sectorsValue}
                    onChange={updateSectors}
                    disabled={fetching}
                    isSelect
                    isMultiSelect
                    selectOptions={sectorOptions || []}
                    selectPlaceholder="Select"
                />
            </div>
            <div style={claimAFacilitySupportDocsFormStyles.inputGroupStyles}>
                <InputLabel htmlFor={numberOfWorkers.id}>
                    <Typography
                        variant="display1"
                        style={yourContactInfoTitleStyle}
                    >
                        {numberOfWorkers.label}
                    </Typography>
                </InputLabel>
                <Typography variant="subheading">
                    {numberOfWorkersDesc.label}
                </Typography>
                <TextField
                    autoFocus
                    id={numberOfWorkers.id}
                    variant="outlined"
                    style={claimAFacilitySupportDocsFormStyles.textFieldStyles}
                    value={numberOfWorkersValue}
                    onChange={updateNumberOfWorkers}
                    disabled={fetching}
                />
            </div>
            <div style={claimAFacilitySupportDocsFormStyles.inputGroupStyles}>
                <InputLabel htmlFor={localLanguageName.id}>
                    <Typography
                        variant="display1"
                        style={yourContactInfoTitleStyle}
                    >
                        {localLanguageName.label}
                    </Typography>
                </InputLabel>
                <Typography variant="subheading">
                    {localLanguageNameDesc.label}
                </Typography>
                <TextField
                    id={localLanguageName.id}
                    variant="outlined"
                    style={claimAFacilitySupportDocsFormStyles.textFieldStyles}
                    value={localLanguageNameValue}
                    onChange={updateLocalLanguageName}
                    disabled={fetching}
                />
            </div>
        </>
    );
}

ClaimFacilityAdditionalData.defaultProps = {
    sectorOptions: null,
};

ClaimFacilityAdditionalData.propTypes = {
    sectorsValue: string.isRequired,
    numberOfWorkersValue: string.isRequired,
    updateNumberOfWorkers: func.isRequired,
    localLanguageNameValue: string.isRequired,
    updateLocalLanguageName: func.isRequired,
    sectorOptions: sectorOptionsPropType,
    fetchSectors: func.isRequired,
    fetching: bool.isRequired,
};

function mapStateToProps({
    claimFacility: {
        claimData: {
            formData: {
                sectorsValue,
                numberOfWorkersValue,
                localLanguageNameValue,
            },
            fetching,
        },
    },
    filterOptions: {
        sectors: { data: sectorOptions, fetching: fetchingSectors },
    },
}) {
    return {
        sectorsValue,
        numberOfWorkersValue,
        localLanguageNameValue,
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
)(ClaimFacilityAdditionalData);
