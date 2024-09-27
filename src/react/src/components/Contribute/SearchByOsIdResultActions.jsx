import React from 'react';
import { object } from 'prop-types';
import { Button } from '@material-ui/core';
import { withStyles } from '@material-ui/core/styles';
import { makeSearchByOsIdResultActionsStyles } from '../../util/styles';

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
    defaultButtonLabel: string.isRequired,
    defaultButtonAction: func.isRequired,
    secondaryButtonLabel: string.isRequired,
    secondaryButtonAction: func.isRequired,
    classes: object.isRequired,
};

export default withStyles(makeSearchByOsIdResultActionsStyles)(
    SearchByOsIdResultActions,
);
