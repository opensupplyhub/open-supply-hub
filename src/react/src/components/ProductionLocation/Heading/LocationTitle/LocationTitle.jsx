import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import get from 'lodash/get';

import productionLocationDetailsTitleStyles from './styles';

const ProductionLocationDetailsTitle = ({ classes, data }) => {
    const locationName = get(data, 'properties.name', '') || '';

    return (
        <div id="overview" className={classes.container}>
            <Typography component="span" className={classes.titleAccent}>
                Location Name
            </Typography>
            <Typography
                component="h1"
                className={classes.title}
                variant="headline"
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
