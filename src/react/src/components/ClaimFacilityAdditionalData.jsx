import React, { useEffect } from 'react';
import { bool, func, string, PropTypes, object } from 'prop-types';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
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

import {
    getValueFromEvent,
    isValidNumberOfWorkers,
    getNumberOfWorkersValidationError,
} from '../util/util';
import {
    claimAFacilitySupportDocsFormStyles,
    textFieldErrorStyles,
} from '../util/styles';

import { claimAFacilityAdditionalDataFormFields } from '../util/constants';

import COLOURS from '../util/COLOURS';
import InputErrorText from './Contribute/InputErrorText';

const infoTitleStyle = Object.freeze({
    paddingBottom: '10px',
    color: COLOURS.NEAR_BLACK,
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
        width: '50%',
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
)(withStyles(textFieldErrorStyles)(ClaimFacilityAdditionalData));
