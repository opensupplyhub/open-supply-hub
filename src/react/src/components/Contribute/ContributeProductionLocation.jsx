import React, { useState } from 'react';
import { withStyles } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsId from './SearchByOsId';
import { makeContributeProductionLocationStyles } from '../../util/styles';

const ContributeProductionLocation = ({ classes }) => {
    const [selectedTab, setSelectedTab] = useState(0);

    const handleChange = (event, value) => {
        setSelectedTab(value);
    };

    return (
        <div className={classes.mainContainerStyles}>
            <Typography
                component="h1"
                variant="h1"
                className={classes.titleStyles}
            >
                Production Location Search
            </Typography>
            <div className={classes.tabsContainerStyles}>
                <Tabs
                    value={selectedTab}
                    onChange={handleChange}
                    classes={{
                        indicator: classes.tabsIndicatorStyles,
                    }}
                >
                    <Tab
                        classes={{
                            root: classes.tabRootStyles,
                            selected: classes.tabSelectedStyles,
                            labelContainer: classes.tabLabelContainerStyles,
                        }}
                        label="Search by OS ID"
                    />
                    <Tab
                        classes={{
                            root: classes.tabRootStyles,
                            selected: classes.tabSelectedStyles,
                            labelContainer: classes.tabLabelContainerStyles,
                        }}
                        label="Search by Name and Address"
                    />
                </Tabs>
                {selectedTab === 0 && <SearchByOsId />}
                {selectedTab === 1 && <div>Search by Name and Address</div>}
            </div>
        </div>
    );
};

export default withStyles(makeContributeProductionLocationStyles)(
    ContributeProductionLocation,
);
