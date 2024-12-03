import React from 'react';
import { connect } from 'react-redux';
import { string, bool, func } from 'prop-types';
import InputLabel from '@material-ui/core/InputLabel';
import ReactSelect from 'react-select';
import { withStyles } from '@material-ui/core/styles';
import { makeFilterStyles, makeSelectFilterStyles } from '../../util/styles';

import CreatableInputOnly from '../CreatableInputOnly';
import CustomDropdownIndicator from './CustomReactSelectComponents/CustomDropdownIndicator';

function StyledSelect({
    name,
    label,
    color,
    creatable,
    classes,
    renderIcon,
    windowWidth,
    isSideBarSearch,
    origin,
    ...rest
}) {
    const selectFilterStyles = makeSelectFilterStyles(
        windowWidth,
        origin,
        color,
    );
    return (
        <>
            {label && (
                <InputLabel
                    shrink={false}
                    htmlFor={name}
                    className={classes.inputLabelStyle}
                >
                    {label} {renderIcon()}
                </InputLabel>
            )}
            {(() => {
                if (creatable)
                    return (
                        <CreatableInputOnly
                            isMulti
                            id={name}
                            name={name}
                            className={`basic-multi-select ${classes.selectStyle}`}
                            classNamePrefix="select"
                            styles={selectFilterStyles}
                            placeholder="Select"
                            {...rest}
                        />
                    );
                if (isSideBarSearch)
                    return (
                        <ReactSelect
                            isMulti
                            id={name}
                            components={{
                                DropdownIndicator: CustomDropdownIndicator,
                                IndicatorSeparator: null,
                            }}
                            name={name}
                            className={`basic-multi-select notranslate ${classes.selectStyle}`}
                            classNamePrefix="select"
                            styles={selectFilterStyles}
                            placeholder="Select"
                            {...rest}
                        />
                    );
                return (
                    <ReactSelect
                        isMulti
                        id={name}
                        components={{
                            DropdownIndicator: CustomDropdownIndicator,
                            IndicatorSeparator: null,
                        }}
                        name={name}
                        className={`basic-multi-select notranslate ${classes.selectStyle}`}
                        classNamePrefix="select"
                        styles={selectFilterStyles}
                        placeholder="Select"
                        menuPosition="fixed"
                        menuPortalTarget={document.body}
                        closeMenuOnScroll={e =>
                            e.target.classList === undefined ||
                            !e.target.classList.contains('select__menu-list')
                        }
                        {...rest}
                    />
                );
            })()}
        </>
    );
}

StyledSelect.defaultProps = {
    creatable: false,
    renderIcon: () => {},
    origin: null,
    label: '',
};

StyledSelect.propTypes = {
    name: string.isRequired,
    label: string,
    creatable: bool,
    renderIcon: func,
    origin: string,
};

function mapStateToProps({
    embeddedMap: { config },
    ui: {
        window: { innerWidth },
    },
}) {
    return {
        color: config?.color,
        windowWidth: innerWidth,
    };
}

export default connect(mapStateToProps)(
    withStyles(makeFilterStyles)(StyledSelect),
);
