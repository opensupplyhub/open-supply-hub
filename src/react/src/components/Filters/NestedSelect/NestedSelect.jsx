import React from 'react';
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
import { useExpandedGroups, useMenuState } from './../../../util/hooks';

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

    const {
        expandedGroups,
        setExpandedGroups,
        handleInputChange,
    } = useExpandedGroups(optionsData);
    const {
        menuIsOpen,
        setMenuIsOpen,
        onMenuOpen,
        onMenuClose,
    } = useMenuState();

    const handleSelect = selected => {
        updateSector(selected);
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
