import React, { useState } from 'react';
import { connect } from 'react-redux';
import ReactSelect from 'react-select';
import { arrayOf, bool, func, number, object, shape, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import CustomDropdownIndicator from './CustomDropdownIndicator';
import CustomGroupHeading from './CustomGroupHeading';
import CustomOption from './CustomOption';
import {
    makeFilterStyles,
    makeNestedSelectFilterStyles,
    makeSelectFilterStyles,
} from '../../../util/styles';

const NestedSelect = ({
    name,
    label,
    optionsData,
    sectors,
    updateSector,
    classes,
    isSideBarSearch,
    windowWidth,
    ...rest
}) => {
    const selectFilterStyles = makeSelectFilterStyles(windowWidth);
    const nestedSelectFilterStyles = makeNestedSelectFilterStyles;
    const combinedStyles = {
        ...selectFilterStyles,
        ...nestedSelectFilterStyles,
    };
    const [menuIsOpen, setMenuIsOpen] = useState(false);
    const [expandedGroups, setExpandedGroups] = useState([]);

    const handleInputChange = inputValue => {
        if (inputValue.trim() === '') {
            setExpandedGroups([]);
            return;
        }

        const newExpandedGroups = optionsData
            .filter(group =>
                group.options.some(option =>
                    option.label
                        .toLowerCase()
                        .includes(inputValue.toLowerCase()),
                ),
            )
            .map(group => group.label);

        setExpandedGroups(newExpandedGroups);
    };

    const handleSelect = selected => {
        updateSector(selected);
    };

    const onMenuOpen = () => {
        setMenuIsOpen(true);
    };

    const onMenuClose = () => {
        setExpandedGroups([]);
        setMenuIsOpen(false);
    };

    const customComponents = {
        GroupHeading: CustomGroupHeading,
        Option: CustomOption,
        DropdownIndicator: CustomDropdownIndicator,
        IndicatorSeparator: null,
    };

    const additionalProps = !isSideBarSearch
        ? {
              menuPosition: 'fixed',
              menuPortalTarget: document.body,
              closeMenuOnScroll: e =>
                  menuIsOpen &&
                  (e.target.classList === undefined ||
                      !e.target.classList.contains('select__menu-list')),
          }
        : {};

    return (
        <>
            <InputLabel
                shrink={false}
                htmlFor={name}
                className={classes.inputLabelStyle}
            >
                {label}
            </InputLabel>

            <ReactSelect
                isMulti
                id={name}
                name={name}
                label={label}
                options={optionsData}
                value={sectors}
                components={customComponents}
                placeholder="Select"
                className={`basic-multi-select notranslate ${classes.selectStyle}`}
                classNamePrefix="select"
                classes={classes}
                styles={combinedStyles}
                expandedGroups={expandedGroups}
                setExpandedGroups={setExpandedGroups}
                selectedOptions={sectors}
                setSelectedOptions={updateSector}
                onChange={handleSelect}
                onMenuClose={onMenuClose}
                onInputChange={handleInputChange}
                onMenuOpen={onMenuOpen}
                menuIsOpen={menuIsOpen}
                setMenuIsOpen={setMenuIsOpen}
                {...additionalProps}
                {...rest}
            />
        </>
    );
};

NestedSelect.propTypes = {
    name: string.isRequired,
    label: string.isRequired,
    optionsData: arrayOf(
        shape({
            label: string.isRequired,
            options: arrayOf(
                shape({
                    groupLabel: string.isRequired,
                    label: string.isRequired,
                    value: string.isRequired,
                }),
            ).isRequired,
        }),
    ).isRequired,
    sectors: arrayOf(
        shape({
            groupLabel: string.isRequired,
            label: string.isRequired,
            value: string.isRequired,
        }),
    ).isRequired,
    updateSector: func.isRequired,
    classes: object.isRequired,
    isSideBarSearch: bool.isRequired,
    windowWidth: number.isRequired,
};

function mapStateToProps({
    ui: {
        window: { innerWidth },
    },
}) {
    return {
        windowWidth: innerWidth,
    };
}

export default connect(mapStateToProps)(
    withStyles(makeFilterStyles)(NestedSelect),
);
