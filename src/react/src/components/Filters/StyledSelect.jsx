import React from 'react';
import { connect } from 'react-redux';
import { string, bool, func } from 'prop-types';
import InputLabel from '@material-ui/core/InputLabel';
import ReactSelect from 'react-select';
import { withStyles } from '@material-ui/core/styles';
import { makeFilterStyles, makeSelectFilterStyles } from '../../util/styles';

import ArrowDropDownIcon from '../ArrowDropDownIcon';
import CreatableInputOnly from '../CreatableInputOnly';

function StyledSelect({
    name,
    label,
    color,
    creatable,
    classes,
    renderIcon,
    windowWidth,
    isSideBarSearch,
    ...rest
}) {
    const selectFilterStyles = makeSelectFilterStyles(windowWidth, color);
    return (
        <>
            <InputLabel
                shrink={false}
                htmlFor={name}
                className={classes.inputLabelStyle}
            >
                {label} {renderIcon()}
            </InputLabel>
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
                                DropdownIndicator: () => (
                                    <div className={classes.dropdownIndicator}>
                                        <ArrowDropDownIcon />
                                    </div>
                                ),
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
                            DropdownIndicator: () => (
                                <div
                                    style={{
                                        display: 'flex',
                                        marginRight: '0.5em',
                                    }}
                                >
                                    <ArrowDropDownIcon />
                                </div>
                            ),
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
};

StyledSelect.propTypes = {
    name: string.isRequired,
    label: string.isRequired,
    creatable: bool,
    renderIcon: func,
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
