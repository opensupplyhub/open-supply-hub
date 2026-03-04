import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Typography from '@material-ui/core/Typography';

import Description from '@material-ui/icons/Description';
import Room from '@material-ui/icons/Room';
import Assignment from '@material-ui/icons/Assignment';
import PlaylistAddCheck from '@material-ui/icons/PlaylistAddCheck';
import VerifiedUser from '@material-ui/icons/VerifiedUser';
import Spa from '@material-ui/icons/Spa';
import AccountBalanceWallet from '@material-ui/icons/AccountBalanceWallet';
import HelpOutline from '@material-ui/icons/HelpOutline';

import navBarStyles from './styles';

const navItems = [
    { to: '#overview', label: 'Overview', Icon: Description },
    { to: '#location', label: 'Location', Icon: Room },
    { to: '#claimed_data', label: 'Claimed data', Icon: Assignment },
    {
        to: '#assessments',
        label: 'Assessments and Audits',
        Icon: PlaylistAddCheck,
    },
    { to: '#certifications', label: 'Certifications', Icon: VerifiedUser },
    { to: '#emissions', label: 'Emissions', Icon: Spa },
    { to: '#living_wage', label: 'Living Wage', Icon: AccountBalanceWallet },
    { to: '#grievance', label: 'Grievance Mechanism', Icon: HelpOutline },
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
