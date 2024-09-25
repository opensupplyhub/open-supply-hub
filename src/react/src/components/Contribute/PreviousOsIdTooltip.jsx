import React, { useState } from 'react';
import { Tooltip, Typography } from '@material-ui/core';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import { withStyles } from '@material-ui/core/styles';
import COLOURS from '../../util/COLOURS';

const arrowGenerator = color => ({
    '&[x-placement*="bottom"] $arrowStyles': {
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
    '&[x-placement*="top"] $arrowStyles': {
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
    '&[x-placement*="right"] $arrowStyles': {
        left: 0,
        marginLeft: '-0.95em',
        height: '3em',
        width: '1em',
        '&::before': {
            borderWidth: '1em 1em 1em 0',
            borderColor: `transparent ${color} transparent transparent`,
        },
    },
    '&[x-placement*="left"] $arrowStyles': {
        right: 0,
        marginRight: '-0.95em',
        height: '3em',
        width: '1em',
        '&::before': {
            borderWidth: '1em 0 1em 1em',
            borderColor: `transparent transparent transparent ${color}`,
        },
    },
});

const makePreviousOsIdTooltipStyles = theme =>
    Object.freeze({
        arrowPopperStyles: arrowGenerator(COLOURS.DARK_SLATE_GRAY),
        arrowStyles: Object.freeze({
            position: 'absolute',
            fontSize: 6,
            width: '22px',
            height: '12px',
            '&::before': {
                content: '""',
                margin: 'auto',
                display: 'block',
                width: 0,
                height: 0,
                borderStyle: 'solid',
            },
        }),
        tooltipStyles: Object.freeze({
            backgroundColor: COLOURS.DARK_SLATE_GRAY,
            color: COLOURS.WHITE,
            maxWidth: '149px',
            boxShadow: '0px 4px 4px 0px #00000040',
        }),
        placementLeftStyles: Object.freeze({
            margin: '0 8px',
        }),
        placementRightStyles: Object.freeze({
            margin: '0 8px',
        }),
        placementTopStyles: Object.freeze({
            margin: '8px 0',
        }),
        placementBottomStyles: Object.freeze({
            margin: '8px 0',
        }),
        tooltipTitleStyles: Object.freeze({
            fontSize: '14px',
            fontWeight: theme.typography.fontWeightMedium,
        }),
        infoOutlinedIconStyles: Object.freeze({
            fontSize: '16px',
            verticalAlign: 'middle',
        }),
    });

const PreviousOsIdTooltip = ({ classes }) => {
    const [arrowRef, setArrowRef] = useState(null);

    return (
        <Tooltip
            title={
                <Typography
                    color="inherit"
                    className={classes.tooltipTitleStyles}
                >
                    This ID was merged into the current ID
                    <span className={classes.arrowStyles} ref={setArrowRef} />
                </Typography>
            }
            classes={{
                popper: classes.arrowPopperStyles,
                tooltip: classes.tooltipStyles,
                tooltipPlacementLeft: classes.placementLeftStyles,
                tooltipPlacementRight: classes.placementRightStyles,
                tooltipPlacementTop: classes.placementTopStyles,
                tooltipPlacementBottom: classes.placementBottomStyles,
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
            <InfoOutlinedIcon className={classes.infoOutlinedIconStyles} />
        </Tooltip>
    );
};

export default withStyles(makePreviousOsIdTooltipStyles)(PreviousOsIdTooltip);
