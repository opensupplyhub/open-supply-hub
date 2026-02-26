import React, { useState, useRef, useCallback } from 'react';
import { shape, string, node, bool } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';
import { makeDialogTooltipStyles } from '../../util/styles';

const LEAVE_TRIGGER_DELAY_MS = 150;

const DialogTooltip = ({
    text,
    childComponent,
    classes,
    interactive = false,
    learnMoreHref,
}) => {
    const [arrowRef, setArrowRef] = useState(null);
    const [open, setOpen] = useState(false);
    const closeTimerRef = useRef(null);

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
        closeTimerRef.current = setTimeout(
            () => setOpen(false),
            LEAVE_TRIGGER_DELAY_MS,
        );
    }, [interactive]);

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
        <>
            {text}
            {learnMoreHref && (
                <p style={{ marginTop: 8, marginBottom: 0 }}>
                    <a
                        href={learnMoreHref}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: 'white' }}
                    >
                        Learn more →
                    </a>
                </p>
            )}
            <span className={classes.arrow} ref={setArrowRef} />
        </>
    );

    const popperProps = interactive
        ? {
              onMouseEnter: handlePopperEnter,
              onMouseLeave: handlePopperLeave,
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
            {childComponent}
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
    learnMoreHref: string,
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
    learnMoreHref: undefined,
};

export default withStyles(makeDialogTooltipStyles)(DialogTooltip);
