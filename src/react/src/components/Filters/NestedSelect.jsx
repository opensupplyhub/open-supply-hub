import React, { useState, useEffect } from 'react';
import { connect } from 'react-redux';
import ReactSelect, { components } from 'react-select';
import InputLabel from '@material-ui/core/InputLabel';
import { withStyles } from '@material-ui/core/styles';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import ChevronRightIcon from '@material-ui/icons/ChevronRight';
import {
    makeFilterStyles,
    makeSelectFilterStyles,
    makeNestedSelectFilterStyles,
} from '../../util/styles';
import ArrowDropDownIcon from '../ArrowDropDownIcon';

const GroupHeading = ({ children, ...props }) => {
    const { label: groupLabel, options: groupOptions, open } = props.data;
    const [isOpen, setIsOpen] = useState(open);

    useEffect(() => {
        setIsOpen(open);
    }, [open]);

    const toggleGroup = () => {
        setIsOpen(prevIsOpen => !prevIsOpen);
    };

    const selectGroup = () => {
        const selectedOptions = props.selectProps.value || [];
        const newSelectedOptions = [
            ...selectedOptions,
            ...groupOptions.filter(
                option =>
                    !selectedOptions.some(
                        selectedOption => selectedOption.value === option.value,
                    ),
            ),
        ];
        props.selectProps.onChange(newSelectedOptions);
    };

    const handleGroupSelectKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            selectGroup();
        }
    };

    const handleToggleKeyDown = event => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            toggleGroup();
        }
    };

    return (
        <>
            <components.GroupHeading {...props}>
                <div
                    onClick={toggleGroup}
                    onKeyDown={handleToggleKeyDown}
                    role="button"
                    tabIndex={0}
                    style={{
                        cursor: 'pointer',
                        display: 'flex',
                    }}
                >
                    {isOpen ? <ExpandMoreIcon /> : <ChevronRightIcon />}
                </div>
                <div
                    onClick={selectGroup}
                    onKeyDown={handleGroupSelectKeyDown}
                    role="button"
                    tabIndex={0}
                >
                    {groupLabel}
                </div>
            </components.GroupHeading>
            {isOpen &&
                groupOptions.map(option => (
                    <components.Option
                        key={option.value}
                        {...props}
                        data={option}
                        innerRef={props.innerRef}
                        innerProps={{
                            ...props.innerProps,
                            onClick: () => {
                                const selectedOptions =
                                    props.selectProps.value || [];
                                const isSelected = selectedOptions.some(
                                    selectedOption =>
                                        selectedOption.value === option.value,
                                );

                                const newSelectedOptions = isSelected
                                    ? selectedOptions.filter(
                                          selectedOption =>
                                              selectedOption.value !==
                                              option.value,
                                      )
                                    : [...selectedOptions, option];

                                props.selectProps.onChange(newSelectedOptions);
                            },
                        }}
                    >
                        {option.label}
                    </components.Option>
                ))}
        </>
    );
};

const MenuList = props => {
    const { children } = props;

    return (
        <components.MenuList {...props}>
            {React.Children.map(children, child => {
                if (
                    child &&
                    child.props &&
                    child.props.data &&
                    child.props.data.options
                ) {
                    return (
                        <GroupHeading
                            {...child.props}
                            key={child.props.data.label}
                            data={child.props.data}
                            selectProps={props.selectProps}
                            innerProps={props.innerProps}
                            innerRef={props.innerRef}
                        />
                    );
                }
                return child;
            })}
        </components.MenuList>
    );
};

const DropdownIndicator = () => (
    <div
        style={{
            display: 'flex',
            marginRight: '0.5em',
        }}
    >
        <ArrowDropDownIcon />
    </div>
);

const NestedSelect = ({
    name,
    label,
    classes,
    optionsData,
    sectors,
    updateSector,
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

    const [inputValue, setInputValue] = useState('');

    const handleChange = options => {
        updateSector(options || []);
        setInputValue('');
    };

    const handleInputChange = value => {
        setInputValue(value);
    };

    const getFilteredOptions = () => {
        const selectedValues = sectors.map(option => option.value);

        return optionsData
            .map(group => ({
                ...group,
                options: group.options.filter(
                    option =>
                        !selectedValues.includes(option.value) &&
                        option.label
                            .toLowerCase()
                            .includes(inputValue.toLowerCase()),
                ),
                open:
                    inputValue.length > 0 &&
                    group.options.some(option =>
                        option.label
                            .toLowerCase()
                            .includes(inputValue.toLowerCase()),
                    ),
            }))
            .filter(group => group.options.length > 0);
    };

    const customComponents = {
        MenuList,
        DropdownIndicator,
        IndicatorSeparator: null,
    };

    const additionalProps = !isSideBarSearch
        ? {
              menuPosition: 'fixed',
              menuPortalTarget: document.body,
              closeMenuOnScroll: e =>
                  e.target.classList === undefined ||
                  !e.target.classList.contains('select__menu-list'),
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
                captureMenuScroll={false}
                components={customComponents}
                name={name}
                options={getFilteredOptions()}
                onChange={handleChange}
                value={sectors}
                isClearable
                inputValue={inputValue}
                onInputChange={handleInputChange}
                placeholder="Select"
                className={`basic-multi-select notranslate ${classes.selectStyle}`}
                classNamePrefix="select"
                styles={combinedStyles}
                {...additionalProps}
                {...rest}
            />
        </>
    );
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
