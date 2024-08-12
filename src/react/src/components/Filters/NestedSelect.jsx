import React, { useState } from 'react';
import { connect } from 'react-redux';
import ReactSelect, { components } from 'react-select';
import { string, arrayOf, shape, func, object, bool, number } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import IconButton from '@material-ui/core/IconButton';
import ButtonBase from '@material-ui/core/ButtonBase';
import {
    makeFilterStyles,
    makeSelectFilterStyles,
    makeNestedSelectFilterStyles,
} from '../../util/styles';
import ArrowDropDownIcon from '../ArrowDropDownIcon';

const GroupHeading = props => {
    const { data, selectProps } = props;
    const {
        expandedGroups,
        setExpandedGroups,
        selectedOptions,
        setSelectedOptions,
        setMenuIsOpen,
        classes,
    } = selectProps;
    const isExpanded = expandedGroups.includes(data.label);

    const handleClick = () => {
        if (isExpanded) {
            setExpandedGroups(
                expandedGroups.filter(label => label !== data.label),
            );
        } else {
            setExpandedGroups([...expandedGroups, data.label]);
        }
    };

    const handleGroupSelect = () => {
        const groupOptions = data.options.map(option => option.value);
        const newSelectedOptions = [
            ...selectedOptions.filter(opt => !groupOptions.includes(opt.value)),
            ...data.options,
        ];
        setSelectedOptions(newSelectedOptions);
        setMenuIsOpen(false);
    };

    return (
        <components.GroupHeading {...props}>
            <IconButton
                onClick={handleClick}
                className={classes.groupHeadingIconButton}
            >
                {isExpanded ? <ExpandMoreIcon /> : <ChevronRightIcon />}
            </IconButton>
            <ButtonBase
                onClick={handleGroupSelect}
                className={classes.groupHeadingButtonBase}
            >
                {data.label}
            </ButtonBase>
        </components.GroupHeading>
    );
};

const Option = props => {
    const { data, selectProps } = props;
    const { expandedGroups } = selectProps;
    const isVisible = expandedGroups.some(group => data.groupLabel === group);

    return isVisible ? <components.Option {...props} /> : null;
};

const DropdownIndicator = ({ selectProps: { classes } }) => (
    <div className={classes.dropdownIndicator}>
        <ArrowDropDownIcon />
    </div>
);

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
        GroupHeading,
        Option,
        DropdownIndicator,
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
