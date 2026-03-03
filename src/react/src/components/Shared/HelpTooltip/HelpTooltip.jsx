import React from 'react';
import PropTypes from 'prop-types';
import Tooltip from '@material-ui/core/Tooltip';
import HelpOutline from '@material-ui/icons/HelpOutline';
import { withStyles } from '@material-ui/core/styles';
import styles from './styles';

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
    title: PropTypes.string.isRequired,
    placement: PropTypes.string,
    enterDelay: PropTypes.number,
    classes: PropTypes.shape({
        popper: PropTypes.string,
        tooltip: PropTypes.string.isRequired,
        icon: PropTypes.string.isRequired,
    }).isRequired,
    className: PropTypes.string,
};

export default withStyles(styles)(HelpTooltip);
