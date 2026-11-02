import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import get from 'lodash/get';

import { CANDIDATE_COPY } from '../../../../util/candidateCopy';
import productionLocationDetailsTitleStyles from './styles';

const ProductionLocationDetailsTitle = ({ classes, data }) => {
    // Candidates are stored with an empty name (design decision D1), so
    // the page shows an interim placeholder instead of a blank heading.
    const isCandidate = !!get(data, 'properties.is_candidate', false);
    const locationName = isCandidate
        ? CANDIDATE_COPY.placeholderName
        : get(data, 'properties.name', '') || '';

    return (
        <div id="overview" className={classes.container}>
            <Typography component="span" className={classes.titleAccent}>
                Location Name
            </Typography>
            <Typography
                component="h1"
                className={classes.title}
                variant="headline"
                data-testid="location-name"
            >
                {locationName}
            </Typography>
        </div>
    );
};

ProductionLocationDetailsTitle.propTypes = {
    classes: PropTypes.object.isRequired,
    data: PropTypes.object,
};

ProductionLocationDetailsTitle.defaultProps = {
    data: null,
};

export default withStyles(productionLocationDetailsTitleStyles)(
    ProductionLocationDetailsTitle,
);
