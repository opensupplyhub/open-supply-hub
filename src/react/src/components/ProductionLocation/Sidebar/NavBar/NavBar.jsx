import React, { useMemo } from 'react';
import { connect } from 'react-redux';

import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Typography from '@material-ui/core/Typography';
import OverviewIcon from '../../../Icons/Overview';
import GeneralInformationIcon from '../../../Icons/GeneralInformation';
import OperationalDetailsIcon from '../../../Icons/OperationalDetails';

import navBarStyles from './styles';
import getIconURL from './utils';

const defaultNavItems = [
    { to: '#overview', label: 'Overview', Icon: OverviewIcon },
    {
        to: '#general-information',
        label: 'General Information',
        Icon: GeneralInformationIcon,
    },
    {
        to: '#operational-details',
        label: 'Operational Details',
        Icon: OperationalDetailsIcon,
    },
];

const NavBar = ({ classes, partnerFieldGroups: { groups } }) => {
    const handleClick = (event, to) => {
        event.preventDefault();
        const id = to.replace('#', '');
        const element = document.getElementById(id);
        if (!element) return;
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    const navItems = useMemo(
        () => [
            ...defaultNavItems,
            ...groups.map(group => ({
                to: `#${group.uuid}`,
                label: group.name,
                Image: () => (
                    <img
                        src={getIconURL(group.icon_file)}
                        width={18}
                        height={18}
                        alt={group.name}
                    />
                ),
            })),
        ],
        [groups],
    );

    return (
        <div className={`${classes.container} ${classes.navContainer}`}>
            <Typography
                variant="title"
                className={classes.title}
                component="h3"
            >
                Jump to
            </Typography>
            <MenuList className={classes.menuList}>
                {navItems.map(({ to, label, Icon, Image, active }) => (
                    <MenuItem
                        key={to}
                        className={`${classes.menuItem} ${
                            active ? classes.menuItemActive : ''
                        }`}
                        disableGutters
                    >
                        <Link
                            to={to}
                            onClick={event => handleClick(event, to)}
                            className={classes.link}
                        >
                            {Image ? (
                                <Image
                                    className={`${classes.menuImage} ${
                                        active ? classes.menuImageActive : ''
                                    }`}
                                />
                            ) : (
                                <Icon
                                    className={`${classes.menuIcon} ${
                                        active ? classes.menuIconActive : ''
                                    }`}
                                />
                            )}
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
};

const mapStateToProps = ({ partnerFieldGroups: { data, fetching } }) => ({
    partnerFieldGroups: {
        groups: data?.results || [],
        fetching,
    },
});

export default connect(mapStateToProps)(withStyles(navBarStyles)(NavBar));
