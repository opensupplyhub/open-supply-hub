import React from 'react';
import { node, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';

import { makeStyledTooltipStyles } from '../util/styles';

const StyledTooltip = ({ classes, children, ...props }) => (
    <Tooltip classes={{ tooltip: classes.tooltip }} {...props}>
        {children}
    </Tooltip>
);

StyledTooltip.propTypes = {
    classes: object.isRequired,
    children: node.isRequired,
};

export default withStyles(makeStyledTooltipStyles)(StyledTooltip);
