import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';
import Chip from '@material-ui/core/Chip';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import COLOURS from '../util/COLOURS';

function arrowGenerator(color) {
    return {
        '&[x-placement*="bottom"] $arrow': {
            top: 0,
            left: 0,
            marginTop: '-0.95em',
            width: '3em',
            height: '1em',
            '&::before': {
                borderWidth: '0 1em 1em 1em',
                borderColor: `transparent transparent ${color} transparent`,
            },
        },
        '&[x-placement*="top"] $arrow': {
            bottom: 0,
            left: 0,
            marginBottom: '-0.95em',
            width: '3em',
            height: '1em',
            '&::before': {
                borderWidth: '1em 1em 0 1em',
                borderColor: `${color} transparent transparent transparent`,
            },
        },
        '&[x-placement*="right"] $arrow': {
            left: 0,
            marginLeft: '-0.95em',
            height: '3em',
            width: '1em',
            '&::before': {
                borderWidth: '1em 1em 1em 0',
                borderColor: `transparent ${color} transparent transparent`,
            },
        },
        '&[x-placement*="left"] $arrow': {
            right: 0,
            marginRight: '-0.95em',
            height: '3em',
            width: '1em',
            '&::before': {
                borderWidth: '1em 0 1em 1em',
                borderColor: `transparent transparent transparent ${color}`,
            },
        },
    };
}

const styles = () => ({
    arrow: {
        position: 'absolute',
        fontSize: 6,
        width: '3em',
        height: '3em',
        '&::before': {
            content: '""',
            margin: 'auto',
            display: 'block',
            width: 0,
            height: 0,
            borderStyle: 'solid',
        },
    },
    bootstrapPopper: arrowGenerator(COLOURS.DARK_SLATE_GREY),
    bootstrapTooltip: {
        fontSize: '14px',
        backgroundColor: COLOURS.DARK_SLATE_GREY,
    },
    bootstrapPlacementLeft: {
        margin: '0 8px',
    },
    bootstrapPlacementRight: {
        margin: '0 8px',
    },
    bootstrapPlacementTop: {
        margin: '8px 0',
    },
    bootstrapPlacementBottom: {
        margin: '8px 0',
    },
});

const DialogTooltip = (text, child) => {
    const [arrowRef, setArrowRef] = useState(null);
    return (
        <Tooltip
            title={
                <>
                    {text}
                    <span
                        className={classes.arrow}
                        ref={setArrowRef}
                    />
                </>
            }
            classes={{
                tooltip: classes.bootstrapTooltip,
                popper: classes.bootstrapPopper,
                tooltipPlacementLeft:
                    classes.bootstrapPlacementLeft,
                tooltipPlacementRight:
                    classes.bootstrapPlacementRight,
                tooltipPlacementTop:
                    classes.bootstrapPlacementTop,
                tooltipPlacementBottom:
                    classes.bootstrapPlacementBottom,
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
            {child}
        </Tooltip>
    );
};

export default withStyles(styles)(Tooltip);
