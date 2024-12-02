import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';
import COLOURS from '../util/COLOURS';

function arrowGenerator(color) {
    return {
        '&[x-placement*="bottom"] $arrow': Object.freeze({
            top: 0,
            left: 0,
            marginTop: '-0.95em',
            width: '3em',
            height: '1em',
            '&::before': Object.freeze({
                borderWidth: '0 1em 1em 1em',
                borderColor: `transparent transparent ${color} transparent`,
            }),
        }),
        '&[x-placement*="top"] $arrow': Object.freeze({
            bottom: 0,
            left: 0,
            marginBottom: '-0.95em',
            width: '3em',
            height: '1em',
            '&::before': Object.freeze({
                borderWidth: '1em 1em 0 1em',
                borderColor: `${color} transparent transparent transparent`,
            }),
        }),
        '&[x-placement*="right"] $arrow': Object.freeze({
            left: 0,
            marginLeft: '-0.95em',
            height: '3em',
            width: '1em',
            '&::before': Object.freeze({
                borderWidth: '1em 1em 1em 0',
                borderColor: `transparent ${color} transparent transparent`,
            }),
        }),
        '&[x-placement*="left"] $arrow': Object.freeze({
            right: 0,
            marginRight: '-0.95em',
            height: '3em',
            width: '1em',
            '&::before': Object.freeze({
                borderWidth: '1em 0 1em 1em',
                borderColor: `transparent transparent transparent ${color}`,
            }),
        }),
    };
}

const styles = () =>
    Object.freeze({
        arrow: Object.freeze({
            position: 'absolute',
            fontSize: 6,
            width: '3em',
            height: '3em',
            '&::before': Object.freeze({
                content: '""',
                margin: 'auto',
                display: 'block',
                width: 0,
                height: 0,
                borderStyle: 'solid',
            }),
        }),
        bootstrapPopper: Object.freeze(arrowGenerator(COLOURS.DARK_SLATE_GREY)),
        bootstrapTooltip: Object.freeze({
            fontSize: '14px',
            backgroundColor: COLOURS.DARK_SLATE_GREY,
        }),
        bootstrapPlacementLeft: Object.freeze({
            margin: '0 8px',
        }),
        bootstrapPlacementRight: Object.freeze({
            margin: '0 8px',
        }),
        bootstrapPlacementTop: Object.freeze({
            margin: '8px 0',
        }),
        bootstrapPlacementBottom: Object.freeze({
            margin: '8px 0',
        }),
    });

const DialogTooltip = ({ text, childComponent, classes }) => {
    const [arrowRef, setArrowRef] = useState(null);
    return (
        <Tooltip
            title={
                <>
                    {text}
                    <span className={classes.arrow} ref={setArrowRef} />
                </>
            }
            classes={{
                tooltip: classes.bootstrapTooltip,
                popper: classes.bootstrapPopper,
                tooltipPlacementLeft: classes.bootstrapPlacementLeft,
                tooltipPlacementRight: classes.bootstrapPlacementRight,
                tooltipPlacementTop: classes.bootstrapPlacementTop,
                tooltipPlacementBottom: classes.bootstrapPlacementBottom,
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

export default withStyles(styles)(DialogTooltip);
