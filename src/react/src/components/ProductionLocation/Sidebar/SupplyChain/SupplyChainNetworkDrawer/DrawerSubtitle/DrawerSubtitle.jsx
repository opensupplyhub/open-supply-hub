import React from 'react';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import drawerSubtitleStyles from './styles';

const DrawerSubtitle = ({ classes, totalCount }) => (
    <Typography className={classes.subtitle} component="p">
        {totalCount}{' '}
        {totalCount === 1 ? 'organization has' : 'organizations have'} shared
        data about this production location
    </Typography>
);

export default withStyles(drawerSubtitleStyles)(DrawerSubtitle);
