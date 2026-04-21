import React from 'react';
import { object, number, func } from 'prop-types';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';

import getSourcesButtonLabel from './utils';
import sourcesButtonStyles from './styles';

const SourcesButton = ({ classes, sourcesCount, onOpenDrawer }) => {
    const sourcesButtonLabel = getSourcesButtonLabel(sourcesCount);

    return (
        <Button
            className={classes.button}
            onClick={onOpenDrawer}
            data-testid="data-point-sources-button"
        >
            {sourcesButtonLabel}
        </Button>
    );
};

SourcesButton.propTypes = {
    classes: object.isRequired,
    sourcesCount: number.isRequired,
    onOpenDrawer: func.isRequired,
};

export default withStyles(sourcesButtonStyles)(SourcesButton);
