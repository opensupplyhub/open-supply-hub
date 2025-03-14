import React from 'react';
import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';

import { makeStyledTooltipStyles } from '../util/styles';

const StyledTooltip = props => <Tooltip {...props} />;

export default withStyles(makeStyledTooltipStyles)(StyledTooltip);
