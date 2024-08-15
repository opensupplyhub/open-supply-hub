import React from 'react';
import ArrowDropDownIcon from '../../ArrowDropDownIcon';

const CustomDropdownIndicator = ({ selectProps: { classes } }) => (
    <div className={classes.dropdownIndicator}>
        <ArrowDropDownIcon />
    </div>
);

export default CustomDropdownIndicator;
