import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsId from './SearchByOsId';

import COLOURS from '../../util/COLOURS';

const makeContributeProductionLocationStyles = theme => ({
    root: {
        flexGrow: 1,
        marginTop: 48,
    },
    tabsIndicator: {
        backgroundColor: theme.palette.primary.main,
        height: '4px',
    },
    tabRoot: {
        textTransform: 'initial',
        fontSize: '18px',
        fontWeight: theme.typography.fontWeightSemiBold,
        width: '100%',
        maxWidth: 300,
        borderBottom: `1px solid ${COLOURS.NEAR_BLACK}`,
        paddingBottom: 16,
        '&$tabSelected': {
            fontWeight: theme.typography.fontWeightBold,
        },
    },
    tabLabelContainer: {
        padding: '0 24px',
    },
    tabSelected: {},
});

const ContributeProductionLocation = ({ classes }) => {
    const [value, setValue] = useState(0);

    const handleChange = (event, v) => {
        setValue(v);
    };

    return (
        <div
            style={{
                background: COLOURS.LIGHT_GREY,
                padding: '48px 5% 120px 5%',
            }}
        >
            <Typography
                component="h1"
                variant="h1"
                style={{
                    fontWeight: '900',
                    fontSize: '56px',
                }}
            >
                Production Location Search
            </Typography>
            <div className={classes.root}>
                <Tabs
                    value={value}
                    onChange={handleChange}
                    classes={{
                        root: classes.tabsRoot,
                        indicator: classes.tabsIndicator,
                    }}
                >
                    <Tab
                        classes={{
                            root: classes.tabRoot,
                            selected: classes.tabSelected,
                            labelContainer: classes.tabLabelContainer,
                        }}
                        label="Search by OS ID"
                    />
                    <Tab
                        classes={{
                            root: classes.tabRoot,
                            selected: classes.tabSelected,
                            labelContainer: classes.tabLabelContainer,
                        }}
                        label="Search by Name and Address"
                    />
                </Tabs>
                {value === 0 && <SearchByOsId />}
                {value === 1 && <div>Search by Name and Address</div>}
            </div>
        </div>
    );
};

ContributeProductionLocation.propTypes = {
    classes: PropTypes.object.isRequired,
};

export default withStyles(makeContributeProductionLocationStyles)(
    ContributeProductionLocation,
);
