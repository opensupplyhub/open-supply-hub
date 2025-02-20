import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsIdTab from './SearchByOsIdTab';
import SearchByNameAndAddressTab from './SearchByNameAndAddressTab';
import { makeContributeProductionLocationStyles } from '../../util/styles';

const TAB_OS_ID = 'os-id';
const TAB_NAME_ADDRESS = 'name-address';
const VALID_TABS = [TAB_OS_ID, TAB_NAME_ADDRESS];

const ContributeProductionLocation = ({ classes }) => {
    const location = useLocation();
    const history = useHistory();

    const queryParams = new URLSearchParams(location.search);
    const tabInQuery = queryParams.get('tab');

    const [selectedTab, setSelectedTab] = useState(
        VALID_TABS.includes(tabInQuery) ? tabInQuery : TAB_NAME_ADDRESS,
    );

    useEffect(() => {
        if (VALID_TABS.includes(tabInQuery)) {
            setSelectedTab(tabInQuery);
        } else {
            history.replace(`?tab=${TAB_NAME_ADDRESS}`);
            setSelectedTab(TAB_NAME_ADDRESS);
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
                        label="Search by Name and Address"
                        value={TAB_NAME_ADDRESS}
                    />
                    <Tab
                        classes={{
                            root: classes.tabRootStyles,
                            selected: classes.tabSelectedStyles,
                            labelContainer: classes.tabLabelContainerStyles,
                        }}
                        label="Search by OS ID"
                        value={TAB_OS_ID}
                    />
                </Tabs>
                {selectedTab === TAB_OS_ID && <SearchByOsIdTab />}
                {selectedTab === TAB_NAME_ADDRESS && (
                    <SearchByNameAndAddressTab />
                )}
            </div>
        </div>
    );
};

export default withStyles(makeContributeProductionLocationStyles)(
    ContributeProductionLocation,
);
