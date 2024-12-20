import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import ArrowDropDownIcon from '../../ArrowDropDownIcon';
import ArrowDropDownUpIcon from '../../ArrowDropDownUpIcon';
import { makeCustomDropdownIndicatorStyles } from '../../../util/styles';

const CustomDropdownIndicator = ({ classes, arrowDown = true }) => (
    <div className={classes.dropdownIndicator}>
        {arrowDown ? <ArrowDropDownIcon /> : <ArrowDropDownUpIcon />}
    </div>
);

export default withStyles(makeCustomDropdownIndicatorStyles)(
    CustomDropdownIndicator,
);
