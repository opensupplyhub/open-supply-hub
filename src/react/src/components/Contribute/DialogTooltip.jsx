import React, { useState } from 'react';
import { shape, string, node } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';
import { makeDialogTooltipStyles } from '../../util/styles';

const DialogTooltip = ({ text, childComponent, classes }) => {
    const [arrowRef, setArrowRef] = useState(null);
    return (
        <Tooltip
            aria-label={text}
            enterDelay={200}
            leaveDelay={200}
            title={
                <>
                    {text}
                    <span className={classes.arrow} ref={setArrowRef} />
                </>
            }
            classes={{
                tooltip: classes.tooltipStyles,
                popper: classes.popperStyles,
                tooltipPlacementLeft: classes.placementLeft,
                tooltipPlacementRight: classes.placementRight,
                tooltipPlacementTop: classes.placementTop,
                tooltipPlacementBottom: classes.placementBottom,
            }}
            PopperProps={{
                popperOptions: {
                    modifiers: {
                        arrow: {
                            enabled: Boolean(arrowRef),
                            element: arrowRef,
                        },
                    },
                },
            }}
        >
            {childComponent}
        </Tooltip>
    );
};

DialogTooltip.propTypes = {
    text: string.isRequired,
    childComponent: node.isRequired,
    classes: shape({
        arrow: shape({}).isRequired,
        tooltipStyles: shape({}).isRequired,
        popperStyles: shape({}).isRequired,
        placementLeft: shape({}).isRequired,
        placementRight: shape({}).isRequired,
        placementTop: shape({}).isRequired,
        placementBottom: shape({}).isRequired,
    }).isRequired,
};

export default withStyles(makeDialogTooltipStyles)(DialogTooltip);
