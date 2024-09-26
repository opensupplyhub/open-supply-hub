import React, { useState, useEffect } from 'react';
import { withStyles } from '@material-ui/core/styles';
import { useLocation, useHistory } from 'react-router-dom';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsId from './SearchByOsId';
import { makeContributeProductionLocationStyles } from '../../util/styles';

const TAB_OS_ID = 'os-id';
const TAB_NAME_ADDRESS = 'name-address';
const VALID_TABS = [TAB_OS_ID, TAB_NAME_ADDRESS];

const ContributeProductionLocation = ({ classes }) => {
    const location = useLocation();
    const history = useHistory();

    const queryParams = new URLSearchParams(location.search);
    const tabInQuery = queryParams.get('tab');

    const [selectedTab, setSelectedTab] = useState(tabInQuery);

    useEffect(() => {
        if (VALID_TABS.includes(tabInQuery)) {
            setSelectedTab(tabInQuery);
        } else {
            history.replace(`?tab=${TAB_OS_ID}`);
            setSelectedTab(TAB_OS_ID);
        }
    }, [tabInQuery, history]);

    const handleChange = (event, value) => {
        setSelectedTab(value);
        history.push(`?tab=${value}`);
    };

    return (
        <div className={classes.mainContainerStyles}>
            <Typography component="h1" className={classes.titleStyles}>
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
                        value={TAB_OS_ID}
                    />
                    <Tab
                        classes={{
                            root: classes.tabRootStyles,
                            selected: classes.tabSelectedStyles,
                            labelContainer: classes.tabLabelContainerStyles,
                        }}
                        label="Search by Name and Address"
                        value={TAB_NAME_ADDRESS}
                    />
                </Tabs>
                {selectedTab === TAB_OS_ID && <SearchByOsId />}
                {selectedTab === TAB_NAME_ADDRESS && (
                    <div>Search by Name and Address</div>
                )}
            </div>
        </div>
    );
};

export default withStyles(makeContributeProductionLocationStyles)(
    ContributeProductionLocation,
);
