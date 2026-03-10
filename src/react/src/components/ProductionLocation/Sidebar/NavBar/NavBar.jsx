import React, { useMemo } from 'react';
import { connect } from 'react-redux';

import { withStyles } from '@material-ui/core/styles';
import { Link } from 'react-router-dom';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Typography from '@material-ui/core/Typography';

import Overview from '../../../Icons/Overview';
import GeneralInformation from '../../../Icons/GeneralInformation';
import OperationalDetails from '../../../Icons/OperationalDetails';

import { setScrollTargetSection } from '../../../../actions/partnerFieldGroups';
import { HEADER_HEIGHT } from '../../../../util/constants';
import navBarStyles from './styles';
import getIconURL from './utils';

const defaultNavItems = [
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

const NavBar = ({ classes, partnerFieldGroups: { groups }, dispatch }) => {
    const groupIds = useMemo(() => groups.map(group => group.uuid), [groups]);

    const handleClick = (event, to) => {
        event.preventDefault();
        const id = to.replace('#', '');

        if (groupIds.includes(id)) {
            dispatch(setScrollTargetSection(id));
            return;
        }

        const element = document.getElementById(id);

        if (element) {
            const top =
                element.getBoundingClientRect().top +
                window.scrollY -
                HEADER_HEIGHT;
            window.scrollTo({ top, behavior: 'smooth' });
        }
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
