import React from 'react';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import { withStyles } from '@material-ui/core/styles';
import CloseIcon from '@material-ui/icons/Close';
import PeopleOutlineIcon from '@material-ui/icons/PeopleOutline';

import DRAWER_TITLE from './constants';
import drawerHeaderStyles from './styles';

const DrawerHeader = ({ classes, onClose }) => (
    <div className={classes.header}>
        <div className={classes.headerLeft}>
            <PeopleOutlineIcon className={classes.titleIcon} />
            <Typography className={classes.title} component="h2">
                {DRAWER_TITLE}
            </Typography>
        </div>
        <IconButton
            className={classes.closeButton}
            aria-label="Close"
            onClick={onClose}
            data-testid="supply-chain-drawer-close"
        >
            <CloseIcon />
        </IconButton>
    </div>
);

export default withStyles(drawerHeaderStyles)(DrawerHeader);
