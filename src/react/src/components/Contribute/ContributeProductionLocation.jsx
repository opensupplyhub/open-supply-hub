import React, { useState, useEffect } from 'react';
import { useLocation, useHistory, Link } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import { bool } from 'prop-types';
import Grid from '@material-ui/core/Grid';
import CircularProgress from '@material-ui/core/CircularProgress';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsIdTab from './SearchByOsIdTab';
import SearchByNameAndAddressTab from './SearchByNameAndAddressTab';
import { makeContributeProductionLocationStyles } from '../../util/styles';
import AppGrid from '../AppGrid';
import { authLoginFormRoute, LOG_IN_TITLE } from '../../util/constants';

const TAB_OS_ID = 'os-id';
const TAB_NAME_ADDRESS = 'name-address';
const VALID_TABS = [TAB_OS_ID, TAB_NAME_ADDRESS];
const TITLE = 'Production Location Search';

const ContributeProductionLocation = ({
    classes,
    userHasSignedIn,
    fetchingSessionSignIn,
}) => {
    const location = useLocation();
    const history = useHistory();

    const queryParams = new URLSearchParams(location.search);
    const tabInQuery = queryParams.get('tab');

    const [selectedTab, setSelectedTab] = useState(
        VALID_TABS.includes(tabInQuery) ? tabInQuery : TAB_OS_ID,
    );

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

    if (fetchingSessionSignIn) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    if (!userHasSignedIn) {
        return (
            <AppGrid title={TITLE}>
                <Grid container className="margin-bottom-64">
                    <Grid item xs={12}>
                        <Link to={authLoginFormRoute} href={authLoginFormRoute}>
                            {LOG_IN_TITLE}
                        </Link>
                    </Grid>
                </Grid>
            </AppGrid>
        );
    }

    return (
        <div className={classes.mainContainerStyles}>
            <Typography component="h1" className={classes.titleStyles}>
                {TITLE}
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

ContributeProductionLocation.propTypes = {
    userHasSignedIn: bool.isRequired,
    fetchingSessionSignIn: bool.isRequired,
};

const mapStateToProps = ({
    contributeProductionLocation: {
        singleProductionLocation: { data, fetching },
    },
    auth: {
        user: { user },
        session: { fetching: fetchingSessionSignIn },
    },
}) => ({
    data,
    fetching,
    userHasSignedIn: !user.isAnon,
    fetchingSessionSignIn,
});

export default connect(mapStateToProps)(
    withStyles(makeContributeProductionLocationStyles)(
        ContributeProductionLocation,
    ),
);
