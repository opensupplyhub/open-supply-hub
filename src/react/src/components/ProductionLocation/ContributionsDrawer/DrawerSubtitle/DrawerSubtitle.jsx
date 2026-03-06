import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import drawerSubtitleStyles from './styles';

const DrawerSubtitle = ({ classes, fieldName, uniqueContributorCount }) => {
    if (fieldName == null || fieldName === '') {
        return null;
    }
    const count = uniqueContributorCount;
    const orgText =
        count === 1 ? '1 organization has' : `${count} organizations have`;
    return (
        <Typography
            className={classes.subtitle}
            component="p"
            data-testid="contributions-drawer-subtitle"
        >
            {orgText} contributed data for{' '}
            <span className={classes.fieldName}>{fieldName}</span>
        </Typography>
    );
};

DrawerSubtitle.propTypes = {
    classes: PropTypes.object.isRequired,
    fieldName: PropTypes.string,
    uniqueContributorCount: PropTypes.number.isRequired,
};

DrawerSubtitle.defaultProps = {
    fieldName: null,
};

export default withStyles(drawerSubtitleStyles)(DrawerSubtitle);
