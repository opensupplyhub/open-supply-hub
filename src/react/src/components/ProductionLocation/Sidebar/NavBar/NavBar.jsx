import React, { useMemo } from 'react';
import { connect } from 'react-redux';

import { withStyles } from '@material-ui/core/styles';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';
import Tab from '@material-ui/icons/Tab';
import Typography from '@material-ui/core/Typography';
import OverviewIcon from '../../../Icons/Overview';
import GeneralInformationIcon from '../../../Icons/GeneralInformation';
import OperationalDetailsIcon from '../../../Icons/OperationalDetails';

import { setScrollTargetSection } from '../../../../actions/partnerFieldGroups';
import { getClaimDisplayData } from '../../../../selectors/claimDataSelectors';
import navBarStyles from './styles';
import { getIconURL, scrollToSection } from './utils';

const NavBar = ({
    classes,
    partnerFieldGroups: { groups },
    dispatch,
    hasOperationalDetails,
}) => {
    const navItems = useMemo(() => {
        function handleOperationalDetailsClick() {
            const id = 'operational-details';
            console.log({ id });
            return event => {
                event.preventDefault();
            };
        }

        function handleGroupClick(id) {
            return event => {
                event.preventDefault();
                dispatch(setScrollTargetSection(id));
            };
        }

        function handleDefaultSectionClick(id) {
            return event => {
                event.preventDefault();
                const element = document.getElementById(id);
                scrollToSection(element);
            };
        }

        return [
            ...[
                {
                    to: '#overview',
                    label: 'Overview',
                    Icon: OverviewIcon,
                    handler: handleDefaultSectionClick('overview'),
                },
                {
                    to: '#general-information',
                    label: 'General Information',
                    Icon: GeneralInformationIcon,
                    handler: handleDefaultSectionClick('general-information'),
                },
            ],
            ...(hasOperationalDetails
                ? [
                      {
                          to: '#operational-details',
                          label: 'Operational Details',
                          Icon: OperationalDetailsIcon,
                          handler: handleOperationalDetailsClick,
                      },
                  ]
                : []),
            ...groups.map(group => ({
                to: `#${group.uuid}`,
                label: group.name,
                handler: handleGroupClick(group.uuid),
                Image: group.icon_file
                    ? () => (
                          <img
                              src={getIconURL(group.icon_file)}
                              width={18}
                              height={18}
                              alt={group.name}
                          />
                      )
                    : () => <Tab style={{ height: 18, width: 18 }} />,
            })),
        ];
    }, [groups, hasOperationalDetails]);

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
                {navItems.map(({ to, label, Icon, Image, active, handler }) => (
                    <MenuItem
                        key={to}
                        className={`${classes.menuItem} ${
                            active ? classes.menuItemActive : ''
                        }`}
                        disableGutters
                        onClick={handler}
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
                    </MenuItem>
                ))}
            </MenuList>
        </div>
    );
};

const mapStateToProps = state => {
    const { data, fetching } = state.partnerFieldGroups;
    const { hasDisplayableFields } = getClaimDisplayData(state);

    return {
        partnerFieldGroups: {
            groups: data?.results || [],
            fetching,
        },
        hasOperationalDetails: hasDisplayableFields,
    };
};

export default connect(mapStateToProps)(withStyles(navBarStyles)(NavBar));
