import React, { useState, useEffect } from 'react';
import { withStyles } from '@material-ui/core/styles';
import { useLocation, useHistory } from 'react-router-dom';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsId from './SearchByOsId';
import { makeContributeProductionLocationStyles } from '../../util/styles';

const ContributeProductionLocation = ({ classes }) => {
    const location = useLocation();
    const history = useHistory();

    const hash = location.hash ? location.hash.substring(1) : '';
    const initialTab = hash === 'name-address' ? 1 : 0;

    const [selectedTab, setSelectedTab] = useState(initialTab);

    useEffect(() => {
        if (!location.hash) {
            history.replace('#os-id');
        }

        const handleHashChange = () => {
            const newHash = window.location.hash.substring(1);
            setSelectedTab(newHash === 'name-address' ? 1 : 0);
        };

        window.addEventListener('hashchange', handleHashChange);
        return () => window.removeEventListener('hashchange', handleHashChange);
    }, [location.hash, history]);

    const handleChange = (event, value) => {
        setSelectedTab(value);
        const newHash = value === 1 ? '#name-address' : '#os-id';
        history.replace(newHash);
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
