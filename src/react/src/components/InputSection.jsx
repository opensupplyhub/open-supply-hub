import React from 'react';
import TextField from '@material-ui/core/TextField';
import InputLabel from '@material-ui/core/InputLabel';
import find from 'lodash/find';
import stubFalse from 'lodash/stubFalse';
import filter from 'lodash/filter';
import includes from 'lodash/includes';
import isNull from 'lodash/isNull';
import Switch from '@material-ui/core/Switch';
import noop from 'lodash/noop';
import map from 'lodash/map';
import Select from 'react-select';
import Creatable from 'react-select/creatable';
import CreatableInputOnly from './CreatableInputOnly';
import ShowOnly from './ShowOnly';
import { getSelectStyles } from '../util/util';

const controlStyles = getSelectStyles();

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
    ...controlStyles,
});

const InputSection = ({
    label,
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
    isClaimFacilityAdditionalDataPage = false,
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

        return isClaimFacilityAdditionalDataPage ? (
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
        ) : (
            <div style={classes.inputSectionStyles}>
                <InputLabel style={classes.inputSectionLabelStyles}>
                    {label}
                </InputLabel>
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
                {isClaimFacilityAdditionalDataPage ? null : label}
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

export default InputSection;
