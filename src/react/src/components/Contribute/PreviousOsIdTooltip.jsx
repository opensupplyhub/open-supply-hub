import React, { useState } from 'react';
import { Tooltip, Typography } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import InfoOutlinedIcon from '@material-ui/icons/InfoOutlined';
import { makePreviousOsIdTooltipStyles } from '../../util/styles';

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
            <InfoOutlinedIcon
                className={classes.infoOutlinedIconStyles}
                data-testid="previous-os-id-tooltip"
            />
        </Tooltip>
    );
};

export default withStyles(makePreviousOsIdTooltipStyles)(PreviousOsIdTooltip);
