import React, { useState, useRef, useCallback, useEffect } from 'react';
import { shape, string, node, bool } from 'prop-types';
import { v4 as uuidv4 } from 'uuid';
import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';
import InteractiveTrigger from './InteractiveTrigger';
import { makeDialogTooltipStyles } from '../../util/styles';

const LEAVE_TRIGGER_DELAY_MS = 150;

const DialogTooltip = ({
    text,
    childComponent,
    classes,
    interactive = false,
    textHref,
}) => {
    const [arrowRef, setArrowRef] = useState(null);
    const [open, setOpen] = useState(false);
    const closeTimerRef = useRef(null);
    const [tooltipId] = useState(() => `dialog-tooltip-${uuidv4()}`);

    const clearCloseTimer = useCallback(() => {
        if (closeTimerRef.current) {
            clearTimeout(closeTimerRef.current);
            closeTimerRef.current = null;
        }
    }, []);

    const handleTriggerEnter = useCallback(() => {
        clearCloseTimer();
        setOpen(true);
    }, [clearCloseTimer]);

    const handleTriggerLeave = useCallback(() => {
        if (!interactive) return;
        clearCloseTimer();
        closeTimerRef.current = setTimeout(
            () => setOpen(false),
            LEAVE_TRIGGER_DELAY_MS,
        );
    }, [interactive, clearCloseTimer]);

    useEffect(() => () => clearCloseTimer(), [clearCloseTimer]);

    const handlePopperEnter = useCallback(() => {
        if (!interactive) return;
        clearCloseTimer();
        setOpen(true);
    }, [interactive, clearCloseTimer]);

    const handlePopperLeave = useCallback(() => {
        if (!interactive) return;
        setOpen(false);
    }, [interactive]);

    const titleContent = (
        <div id={tooltipId} role="tooltip">
            {text}
            {textHref}
            <span className={classes.arrow} ref={setArrowRef} />
        </div>
    );

    const arrowModifier = {
        enabled: Boolean(arrowRef),
        element: arrowRef,
    };
    const popperProps = {
        popperOptions: {
            modifiers: { arrow: arrowModifier },
        },
    };
    if (interactive) {
        popperProps.onMouseEnter = handlePopperEnter;
        popperProps.onMouseLeave = handlePopperLeave;
        popperProps.onFocus = handlePopperEnter;
        popperProps.onBlur = handlePopperLeave;
    }

    const triggerWrapper = interactive ? (
        <InteractiveTrigger
            childComponent={childComponent}
            tooltipId={tooltipId}
            onEnter={handleTriggerEnter}
            onLeave={handleTriggerLeave}
        />
    ) : (
        childComponent
    );

    return (
        <Tooltip
            enterDelay={interactive ? 0 : 200}
            leaveDelay={interactive ? 0 : 200}
            interactive={interactive}
            open={interactive ? open : undefined}
            onClose={interactive ? () => setOpen(false) : undefined}
            title={titleContent}
            classes={{
                tooltip: classes.tooltipStyles,
                popper: classes.popperStyles,
                tooltipPlacementLeft: classes.placementLeft,
                tooltipPlacementRight: classes.placementRight,
                tooltipPlacementTop: classes.placementTop,
                tooltipPlacementBottom: classes.placementBottom,
            }}
            PopperProps={popperProps}
        >
            {triggerWrapper}
        </Tooltip>
    );
};

DialogTooltip.propTypes = {
    text: string.isRequired,
    childComponent: node.isRequired,
    interactive: bool,
    textHref: node,
    classes: shape({
        arrow: string.isRequired,
        tooltipStyles: string.isRequired,
        popperStyles: string.isRequired,
        placementLeft: string.isRequired,
        placementRight: string.isRequired,
        placementTop: string.isRequired,
        placementBottom: string.isRequired,
    }).isRequired,
};

DialogTooltip.defaultProps = {
    interactive: false,
    textHref: null,
};

export default withStyles(makeDialogTooltipStyles)(DialogTooltip);
