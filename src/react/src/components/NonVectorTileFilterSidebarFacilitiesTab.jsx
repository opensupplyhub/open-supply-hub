import React, { Fragment, useState } from 'react';
import { arrayOf, bool, func, number, string } from 'prop-types';
import { connect } from 'react-redux';
import { Link } from 'react-router-dom';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import { withStyles } from '@material-ui/core/styles';
import get from 'lodash/get';
import InfiniteAnyHeight from 'react-infinite-any-height';
import includes from 'lodash/includes';
import lowerCase from 'lodash/lowerCase';

import ControlledTextInput from './ControlledTextInput';

import {
    toggleFilterModal,
    updateSidebarFacilitiesTabTextFilter,
} from '../actions/ui';

import { facilityCollectionPropType, userPropType } from '../util/propTypes';

import { makeFacilityDetailLink, getValueFromEvent } from '../util/util';

import COLOURS from '../util/COLOURS';

import { filterSidebarStyles } from '../util/styles';
import DownloadButtonWithFlags from './DownloadButtonWithFlags';
import LoginRequiredDialog from './LoginRequiredDialog';

const SEARCH_TERM_INPUT = 'SEARCH_TERM_INPUT';

const caseInsensitiveIncludes = (target, test) =>
    includes(lowerCase(target), lowerCase(test));

const sortFacilitiesAlphabeticallyByName = data =>
    data
        .slice()
        .sort(
            (
                { properties: { name: firstFacilityName } },
                { properties: { name: secondFacilityName } },
            ) => {
                const a = lowerCase(firstFacilityName);
                const b = lowerCase(secondFacilityName);

                if (a === b) {
                    return 0;
                }

                return a < b ? -1 : 1;
            },
        );

const makeFacilitiesTabStyles = theme => ({
    noResultsTextStyles: Object.freeze({
        fontFamily: theme.typography.fontFamily,
        margin: '30px',
    }),
    linkStyles: Object.freeze({
        display: 'flex',
        textDecoration: 'none',
        fontFamily: theme.typography.fontFamily,
    }),
    listItemStyles: Object.freeze({
        wordWrap: 'anywhere',
        fontFamily: theme.typography.fontFamily,
    }),
    listHeaderStyles: Object.freeze({
        backgroundColor: COLOURS.WHITE,
        padding: '0.25rem',
        maxHeight: '130px',
    }),
    titleRowStyles: Object.freeze({
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '6px 1rem',
    }),
    listHeaderTextSearchStyles: Object.freeze({
        padding: '6px 1rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    }),
});

function NonVectorTileFilterSidebarFacilitiesTab({
    fetching,
    data,
    error,
    windowHeight,
    embed,
    returnToSearchTab,
    filterText,
    updateFilterText,
    classes,
    user,
    isSameContributor,
}) {
    const [loginRequiredDialogIsOpen, setLoginRequiredDialogIsOpen] = useState(
        false,
    );

    if (fetching) {
        return (
            <div
                className="control-panel__content"
                style={filterSidebarStyles.controlPanelContentStyles}
            >
                <div className="control-panel__body">
                    <CircularProgress />
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div
                className="control-panel__content"
                style={filterSidebarStyles.controlPanelContentStyles}
            >
                <div className="control-panel__body">
                    <Typography
                        variant="body1"
                        className={classes.noResultsTextStyles}
                        align="center"
                    >
                        An error prevented fetching facilities
                    </Typography>
                    <Typography
                        variant="body1"
                        className={classes.noResultsTextStyles}
                        align="center"
                    >
                        <Button
                            onClick={returnToSearchTab}
                            variant="outlined"
                            color="secondary"
                        >
                            Try another search
                        </Button>
                    </Typography>
                </div>
            </div>
        );
    }

    const facilities = get(data, 'features', []);

    if (!facilities.length) {
        return (
            <div
                className="control-panel__content"
                style={filterSidebarStyles.controlPanelContentStyles}
            >
                <div className="control-panel__body">
                    <Typography
                        variant="body1"
                        className={classes.noResultsTextStyles}
                        align="center"
                    >
                        No facilities to display
                    </Typography>
                    <Typography
                        variant="body1"
                        className={classes.noResultsTextStyles}
                        align="center"
                    >
                        <Button
                            onClick={returnToSearchTab}
                            variant="outlined"
                            color="secondary"
                        >
                            Search for facilities
                        </Button>
                    </Typography>
                </div>
            </div>
        );
    }

    const filteredFacilities = filterText
        ? facilities.filter(
              ({ properties: { address, name, country_name: countryName } }) =>
                  caseInsensitiveIncludes(address, filterText) ||
                  caseInsensitiveIncludes(name, filterText) ||
                  caseInsensitiveIncludes(countryName, filterText),
          )
        : facilities;

    const orderedFacilities = sortFacilitiesAlphabeticallyByName(
        filteredFacilities,
    );

    const facilitiesCount = get(data, 'count', null);

    const headerDisplayString =
        facilitiesCount && facilitiesCount !== filteredFacilities.length
            ? `Displaying ${filteredFacilities.length} facilities of ${facilitiesCount} results`
            : `Displaying ${filteredFacilities.length} facilities`;

    const listHeaderInsetComponent = (
        <div className={`${classes.listHeaderStyles} results-height-subtract`}>
            <Typography variant="subheading" align="center">
                <div className={classes.titleRowStyles}>
                    {headerDisplayString}
                    <DownloadButtonWithFlags
                        embed={!!embed}
                        facilitiesCount={facilitiesCount}
                        isSameContributor={!!isSameContributor}
                        userAllowedRecords={user.allowed_records_number}
                        setLoginRequiredDialogIsOpen={
                            setLoginRequiredDialogIsOpen
                        }
                    />
                </div>
            </Typography>
            <div className={classes.listHeaderTextSearchStyles}>
                <label htmlFor={SEARCH_TERM_INPUT}>Filter results</label>
                <ControlledTextInput
                    id={SEARCH_TERM_INPUT}
                    value={filterText}
                    onChange={updateFilterText}
                    placeholder="Filter by name, address, or country"
                />
            </div>
        </div>
    );

    const nonResultListComponentHeight = Array.from(
        document.getElementsByClassName('results-height-subtract'),
    ).reduce((sum, x) => sum + x.offsetHeight, 0);

    const resultListHeight = windowHeight - nonResultListComponentHeight;

    return (
        <Fragment>
            {listHeaderInsetComponent}
            <div style={filterSidebarStyles.controlPanelContentStyles}>
                <List>
                    <InfiniteAnyHeight
                        containerHeight={resultListHeight}
                        list={orderedFacilities.map(
                            ({
                                properties: {
                                    address,
                                    name,
                                    country_name: countryName,
                                    os_id: osID,
                                },
                            }) => (
                                <Fragment key={osID}>
                                    <Divider />
                                    <ListItem
                                        key={osID}
                                        className={classes.listItemStyles}
                                    >
                                        <Link
                                            to={{
                                                pathname: makeFacilityDetailLink(
                                                    osID,
                                                ),
                                                state: {
                                                    panMapToFacilityDetails: true,
                                                },
                                            }}
                                            href={makeFacilityDetailLink(osID)}
                                            className={classes.linkStyles}
                                        >
                                            <ListItemText
                                                primary={`${name} - ${countryName}`}
                                                secondary={address}
                                            />
                                        </Link>
                                    </ListItem>
                                </Fragment>
                            ),
                        )}
                    />
                </List>
            </div>
            <LoginRequiredDialog
                open={loginRequiredDialogIsOpen}
                onClose={() => setLoginRequiredDialogIsOpen(false)}
            />
        </Fragment>
    );
}

NonVectorTileFilterSidebarFacilitiesTab.defaultProps = {
    data: null,
    error: null,
    user: null,
    isSameContributor: false,
};

NonVectorTileFilterSidebarFacilitiesTab.propTypes = {
    data: facilityCollectionPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
    windowHeight: number.isRequired,
    returnToSearchTab: func.isRequired,
    filterText: string.isRequired,
    updateFilterText: func.isRequired,
    embed: bool.isRequired,
    user: userPropType,
    isSameContributor: bool,
};

function mapStateToProps({
    facilities: {
        facilities: { data, error, fetching },
    },
    ui: {
        facilitiesSidebarTabSearch: { filterText },
        window: { innerHeight: windowHeight },
    },
    auth: {
        user: { user },
    },
    embeddedMap: { embed },
}) {
    return {
        user,
        data,
        error,
        fetching,
        filterText,
        windowHeight,
        embed: !!embed,
        isSameContributor: get(data, 'is_same_contributor', false),
    };
}

function mapDispatchToProps(dispatch) {
    return {
        returnToSearchTab: () => dispatch(toggleFilterModal()),
        updateFilterText: e =>
            dispatch(
                updateSidebarFacilitiesTabTextFilter(getValueFromEvent(e)),
            ),
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(makeFacilitiesTabStyles)(NonVectorTileFilterSidebarFacilitiesTab));
