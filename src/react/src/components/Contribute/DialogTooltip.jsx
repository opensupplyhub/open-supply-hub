import React, { useState, useRef, useCallback, useEffect } from 'react';
import { shape, string, node, bool } from 'prop-types';
import { v4 as uuidv4 } from 'uuid';
import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';
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

    const popperProps = interactive
        ? {
              onMouseEnter: handlePopperEnter,
              onMouseLeave: handlePopperLeave,
              onFocus: handlePopperEnter,
              onBlur: handlePopperLeave,
              popperOptions: {
                  modifiers: {
                      arrow: {
                          enabled: Boolean(arrowRef),
                          element: arrowRef,
                      },
                  },
              },
          }
        : {
              popperOptions: {
                  modifiers: {
                      arrow: {
                          enabled: Boolean(arrowRef),
                          element: arrowRef,
                      },
                  },
              },
          };

    const triggerWrapper = interactive ? (
        <span
            onMouseEnter={handleTriggerEnter}
            onMouseLeave={handleTriggerLeave}
            style={{ display: 'inline-flex' }}
        >
            {React.isValidElement(childComponent) ? (
                React.cloneElement(childComponent, {
                    onFocus: e => {
                        handleTriggerEnter();
                        childComponent.props.onFocus?.(e);
                    },
                    onBlur: e => {
                        handleTriggerLeave();
                        childComponent.props.onBlur?.(e);
                    },
                    onKeyDown: e => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            handleTriggerEnter();
                        }
                        childComponent.props.onKeyDown?.(e);
                    },
                    'aria-describedby': tooltipId,
                })
            ) : (
                <button
                    type="button"
                    onFocus={handleTriggerEnter}
                    onBlur={handleTriggerLeave}
                    onKeyDown={e => {
                        if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            handleTriggerEnter();
                        }
                    }}
                    aria-describedby={tooltipId}
                    style={{
                        display: 'inline',
                        margin: 0,
                        padding: 0,
                        border: 'none',
                        background: 'none',
                        font: 'inherit',
                    }}
                >
                    {childComponent}
                </button>
            )}
        </span>
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
