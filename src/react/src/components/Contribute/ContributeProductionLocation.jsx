import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from 'react-router-dom';
import { withStyles } from '@material-ui/core/styles';
import { connect } from 'react-redux';
import { bool, string, shape } from 'prop-types';
import CircularProgress from '@material-ui/core/CircularProgress';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Typography from '@material-ui/core/Typography';
import SearchByOsIdTab from './SearchByOsIdTab';
import SearchByNameAndAddressTab from './SearchByNameAndAddressTab';
import AuthLogInFromRoute from '../AuthLogInFromRoute';
import { makeContributeProductionLocationStyles } from '../../util/styles';

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

    if (fetchingSessionSignIn) {
        return (
            <div className={classes.circularProgressContainerStyles}>
                <CircularProgress />
            </div>
        );
    }

    if (!userHasSignedIn) {
        return <AuthLogInFromRoute title={TITLE} />;
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
    classes: shape({
        circularProgressContainerStyles: string,
        mainContainerStyles: string.isRequired,
        titleStyles: string.isRequired,
        tabsContainerStyles: string.isRequired,
        tabsIndicatorStyles: string.isRequired,
        tabRootStyles: string.isRequired,
        tabSelectedStyles: string.isRequired,
        tabLabelContainerStyles: string.isRequired,
    }).isRequired,
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
