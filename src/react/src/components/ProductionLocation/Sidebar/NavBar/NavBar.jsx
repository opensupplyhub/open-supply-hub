import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Typography from '@material-ui/core/Typography';

import Overview from '../../../Icons/Overview';
import GeneralInformation from '../../../Icons/GeneralInformation';
import OperationalDetails from '../../../Icons/OperationalDetails';

import navBarStyles from './styles';

const navItems = [
    { to: '#overview', label: 'Overview', Icon: Overview },
    {
        to: '#general-information',
        label: 'General Information',
        Icon: GeneralInformation,
    },
    {
        to: '#operational-details',
        label: 'Operational Details',
        Icon: OperationalDetails,
    },
];

const NavBar = ({ classes }) => (
    <div className={`${classes.container} ${classes.navContainer}`}>
        <Typography variant="title" className={classes.title} component="h3">
            Jump to
        </Typography>
        <MenuList className={classes.menuList}>
            {navItems.map(({ to, label, Icon, active }) => (
                <MenuItem
                    key={to}
                    className={`${classes.menuItem} ${
                        active ? classes.menuItemActive : ''
                    }`}
                    disableGutters
                >
                    <Link to={to} className={classes.link}>
                        <Icon
                            className={`${classes.menuIcon} ${
                                active ? classes.menuIconActive : ''
                            }`}
                        />
                        <Typography
                            variant="body1"
                            className={`${classes.menuLabel} ${
                                active ? classes.menuLabelActive : ''
                            }`}
                        >
                            {label}
                        </Typography>
                    </Link>
                </MenuItem>
            ))}
        </MenuList>
    </div>
);

export default withStyles(navBarStyles)(NavBar);
