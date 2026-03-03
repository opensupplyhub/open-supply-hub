import React from 'react';
import { string, number, shape } from 'prop-types';
import Tooltip from '@material-ui/core/Tooltip';
import HelpOutline from '@material-ui/icons/HelpOutline';
import { withStyles } from '@material-ui/core/styles';
import helpTooltipStyles from './styles';

const HelpTooltip = ({ title, placement, enterDelay, classes, className }) => (
    <Tooltip
        title={title}
        placement={placement}
        enterDelay={enterDelay}
        classes={{ popper: classes.popper, tooltip: classes.tooltip }}
    >
        <span className={`${className} ${classes.defaultTooltipIcon}`}>
            <HelpOutline
                className={classes.icon}
                fontSize="small"
                aria-label={title}
            />
        </span>
    </Tooltip>
);

HelpTooltip.defaultProps = {
    placement: 'top',
    enterDelay: 0,
    className: undefined,
};

HelpTooltip.propTypes = {
    title: string.isRequired,
    placement: string,
    enterDelay: number,
    classes: shape({
        popper: string,
        tooltip: string.isRequired,
        icon: string.isRequired,
    }).isRequired,
    className: string,
};

export default withStyles(helpTooltipStyles)(HelpTooltip);
