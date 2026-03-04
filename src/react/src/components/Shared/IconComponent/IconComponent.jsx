import React from 'react';
import {
    string,
    number,
    shape,
    elementType,
    oneOfType,
    node,
} from 'prop-types';
import Tooltip from '@material-ui/core/Tooltip';
import HelpOutline from '@material-ui/icons/HelpOutline';
import { withStyles } from '@material-ui/core/styles';

import useInteractiveTooltip from './hooks';
import iconComponentStyles from './styles';

const IconComponent = ({
    title,
    placement,
    enterDelay,
    classes,
    className,
    icon: Icon,
}) => {
    const {
        open,
        setOpen,
        handleTriggerEnter,
        handleTriggerLeave,
        handlePopperEnter,
        handlePopperLeave,
    } = useInteractiveTooltip();

    return (
        <Tooltip
            title={title}
            placement={placement}
            enterDelay={enterDelay}
            leaveDelay={0}
            open={open}
            onClose={() => setOpen(false)}
            classes={{ popper: classes.popper, tooltip: classes.tooltip }}
            PopperProps={{
                onMouseEnter: handlePopperEnter,
                onMouseLeave: handlePopperLeave,
            }}
        >
            <span
                className={`${className || ''} ${classes.defaultTooltipIcon} ${
                    open && classes.tooltipVisible
                }`}
                onMouseEnter={handleTriggerEnter}
                onMouseLeave={handleTriggerLeave}
            >
                <Icon className={classes.icon} fontSize="small" />
            </span>
        </Tooltip>
    );
};

IconComponent.defaultProps = {
    placement: 'top',
    enterDelay: 0,
    className: undefined,
    icon: HelpOutline,
};

IconComponent.propTypes = {
    title: oneOfType([string, node]).isRequired,
    placement: string,
    enterDelay: number,
    classes: shape({
        popper: string,
        tooltip: string.isRequired,
        defaultTooltipIcon: string,
        icon: string.isRequired,
    }).isRequired,
    className: string,
    icon: elementType,
};

export default withStyles(iconComponentStyles)(IconComponent);
