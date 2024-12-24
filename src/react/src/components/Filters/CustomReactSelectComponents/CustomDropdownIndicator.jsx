import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import ArrowDropDownIcon from '../../ArrowDropDownIcon';
import { makeCustomDropdownIndicatorStyles } from '../../../util/styles';

const CustomDropdownIndicator = ({ classes }) => (
    <div className={classes.dropdownIndicator}>
        <ArrowDropDownIcon />
    </div>
);

export default withStyles(makeCustomDropdownIndicatorStyles)(
    CustomDropdownIndicator,
);
