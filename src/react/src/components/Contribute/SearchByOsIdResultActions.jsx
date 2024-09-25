import React from 'react';
import { object } from 'prop-types';
import { Button } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import COLOURS from '../../util/COLOURS';

const makeSearchByOsIdResultActionsStyles = theme =>
    Object.freeze({
        actionsStyles: Object.freeze({
            display: 'flex',
            gap: '24px',
        }),
        buttonLabelStyles: Object.freeze({
            fontSize: '18px',
            lineHeight: '20px',
            fontWeight: theme.typography.fontWeightExtraBold,
            letterSpacing: '-0.05px',
        }),
        buttonBaseStyles: Object.freeze({
            width: '265px',
            height: '49px',
            borderRadius: '0',
            textTransform: 'none',
        }),
        defaultButtonStyles: Object.freeze({
            borderColor: COLOURS.NEAR_BLACK,
        }),
        secondaryButtonStyles: Object.freeze({
            backgroundColor: theme.palette.action.main,
            color: theme.palette.getContrastText(theme.palette.action.main),
            '&:hover': {
                backgroundColor: theme.palette.action.dark,
            },
        }),
    });

const SearchByOsIdResultActions = ({
    defaultButtonLabel,
    defaultButtonAction,
    secondaryButtonLabel,
    secondaryButtonAction,
    classes,
}) => (
    <div className={classes.actionsStyles}>
        <Button
            variant="outlined"
            classes={{
                root: `${classes.buttonBaseStyles} ${classes.defaultButtonStyles}`,
                label: classes.buttonLabelStyles,
            }}
            onClick={defaultButtonAction}
        >
            {defaultButtonLabel}
        </Button>
        <Button
            variant="contained"
            color="secondary"
            classes={{
                root: `${classes.buttonBaseStyles} ${classes.secondaryButtonStyles}`,
                label: classes.buttonLabelStyles,
            }}
            onClick={secondaryButtonAction}
        >
            {secondaryButtonLabel}
        </Button>
    </div>
);

SearchByOsIdResultActions.propTypes = {
    classes: object.isRequired,
};

export default withStyles(makeSearchByOsIdResultActionsStyles)(
    SearchByOsIdResultActions,
);
