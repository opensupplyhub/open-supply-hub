import React from 'react';
import { object, shape, string } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';

import styles from './styles';
import useSourceByHtmlAnalytics from './hooks';

const SourceByHtmlBlock = ({ sourceBy, classes, gaSpotlightAnalytics }) => {
    const handleClick = useSourceByHtmlAnalytics(gaSpotlightAnalytics);

    return (
        <Typography
            className={classes.root}
            component="div"
            data-testid="facility-details-source-by"
            dangerouslySetInnerHTML={{ __html: sourceBy }}
            onClick={handleClick}
        />
    );
};

SourceByHtmlBlock.propTypes = {
    sourceBy: string.isRequired,
    classes: shape({
        root: string,
    }).isRequired,
    gaSpotlightAnalytics: object,
};

SourceByHtmlBlock.defaultProps = {
    gaSpotlightAnalytics: null,
};

export default withStyles(styles)(SourceByHtmlBlock);
