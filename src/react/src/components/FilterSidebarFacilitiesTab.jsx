import React, { useEffect, useState } from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import { withRouter } from 'react-router';
import { Link } from 'react-router-dom';
import CircularProgress from '@material-ui/core/CircularProgress';
import LinearProgress from '@material-ui/core/LinearProgress';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import Grid from '@material-ui/core/Grid';
import Checkbox from '@material-ui/core/Checkbox';
import { withStyles } from '@material-ui/core/styles';
import get from 'lodash/get';
import InfiniteAnyHeight from 'react-infinite-any-height';
import noop from 'lodash/noop';

import CopySearch from './CopySearch';
import FeatureFlag from './FeatureFlag';
import DownloadFacilitiesButton from './DownloadFacilitiesButton';
import ShowOnly from './ShowOnly';

import {
    toggleFilterModal,
    toggleMergeModal,
    reportListScroll,
} from '../actions/ui';

import { fetchNextPageOfFacilities } from '../actions/facilities';

import {
    updateMergeTargetFacilityOSID,
    fetchMergeTargetFacility,
    updateFacilityToMergeOSID,
    fetchFacilityToMerge,
} from '../actions/mergeFacilities';

import { facilityCollectionPropType, userPropType } from '../util/propTypes';

import {
    REPORT_A_FACILITY,
    authLoginFormRoute,
    authRegisterFormRoute,
    ALLOW_LARGE_DOWNLOADS,
    FACILITIES_DOWNLOAD_DEFAULT_LIMIT,
} from '../util/constants';

import { makeFacilityDetailLink } from '../util/util';
import { useMergeButtonClickHandler } from '../util/hooks';

import COLOURS from '../util/COLOURS';

import { filterSidebarStyles } from '../util/styles';
import BadgeClaimed from './BadgeClaimed';
import CopyLinkIcon from './CopyLinkIcon';
import { useResultListHeight } from '../util/useHeightSubtract';

const makeFacilitiesTabStyles = theme => ({
    noResultsTextStyles: Object.freeze({
        margin: '30px !important',
        fontFamily: theme.typography.fontFamily,
    }),
    facilityLinkWrapper: {
        width: '100%',
    },
    linkStyles: Object.freeze({
        color: '#191919',
        flexDirection: 'column',
        display: 'flex',
        overflow: 'hidden',
        textDecoration: 'none',
        fontFamily: theme.typography.fontFamily,
    }),
    listItemStyles: Object.freeze({
        alignItems: 'start',
        maxWidth: '750px',
        minWidth: '310px',
        wordWrap: 'anywhere',
        [theme.breakpoints.up('sm')]: {
            minWidth: '240px',
        },
        [theme.breakpoints.up('md')]: {
            minWidth: '310px',
        },
    }),
    listItemLoadingPlaceholder: Object.freeze({
        maxWidth: '750px',
        minWidth: '310px',
        [theme.breakpoints.up('sm')]: {
            minWidth: '240px',
        },
        [theme.breakpoints.up('md')]: {
            minWidth: '310px',
        },
    }),
    mergeCheckbox: {
        marginLeft: '-12px',
        color: '#FFA6D0',
    },
    listHeaderStyles: Object.freeze({
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        maxHeight: '173px',
        padding: '0.25rem 1.25rem',
        backgroundColor: COLOURS.WHITE,
    }),
    regularButtonsContainer: {
        width: 'fit-content',
        alignItems: 'center',
    },
    listHeaderButtonStyles: Object.freeze({
        height: '45px',
        margin: '5px 0',
    }),
    downloadLabelStyles: Object.freeze({
        margin: '5px 0',
    }),
    closureRibbon: Object.freeze({
        marginTop: '5px',
        display: 'inline-block',
        padding: '0 5px',
        color: 'rgb(85, 43, 12)',
        fontSize: '14px',
        fontWeight: 'bold',
        fontFamily: theme.typography.fontFamily,
        background: 'rgb(255, 218, 162)',
        borderRadius: '4px',
        border: '1px solid rgb(134, 65, 15)',
    }),
    copyLinkButton: {
        margin: '5px 16px 5px 0',
        height: '45px',
        fontSize: '16px',
        fontWeight: '900',
        lineHeight: '20px',
    },
    copyLinkButtonContent: {
        display: 'flex',
        alignItems: 'center',
        textTransform: 'none',
        whiteSpace: 'nowrap',
    },
    mergeButton: {
        margin: '5px 0',
        padding: '11.5px 16px',
        fontSize: '16px',
        fontWeight: '900',
        lineHeight: '20px',
        color: theme.palette.secondary.contrastText,
        textTransform: 'none',
        border: '1px solid rgba(0, 0, 0, 0.23)',
        backgroundColor: 'rgb(255, 166, 208)',
        '&:hover': {
            backgroundColor: 'rgb(209, 130, 166)',
        },
        '&[disabled]': {
            backgroundColor: 'rgba(0, 0, 0, 0.12)',
        },
    },
    facilityDetailContainer: {
        marginLeft: '-16px',
        fontWeight: 700,
        fontSize: '20px',
    },
    facilityDetailItem: {
        position: 'relative',
        marginLeft: '16px',
        '&::before': {
            content: "'⦁'",
            position: 'absolute',
            left: '-11.5px',
        },
    },
});

function FilterSidebarFacilitiesTab({
    user,
    fetching,
    data,
    error,
    downloadingCSV,
    downloadData,
    returnToSearchTab,
    openMergeModal,
    fetchNextPage,
    isInfiniteLoading,
    targetFacilityOSID,
    facilityToMergeOSID,
    history: {
        location: { search },
    },
    handleScroll,
    scrollTop,
    embed,
    updateToMergeOSID,
    fetchToMergeFacility,
    updateTargetOSID,
    fetchTargetFacility,
    classes,
}) {
    const [loginRequiredDialogIsOpen, setLoginRequiredDialogIsOpen] = useState(
        false,
    );

    const [hasScrolled, setHasScrolled] = useState(false);
    const scrollElements = Array.from(
        document.getElementsByClassName('infinite-scroll'),
    );
    if (!hasScrolled && scrollElements.length) {
        setHasScrolled(true);
        // The timeout allows persisted data to be restored before scroll is attemped
        setTimeout(() => {
            scrollElements.forEach(x => {
                x.scrollTo(0, scrollTop);
            });
        }, 100);
    }

    const resultListHeight = useResultListHeight();

    const [facilitiesToMerge, setFacilitiesToMerge] = useState([]);

    useEffect(() => {
        setFacilitiesToMerge([]);
    }, [fetching]);

    const handleCheckboxChange = osID => {
        if (facilitiesToMerge.length < 2 || facilitiesToMerge.includes(osID)) {
            setFacilitiesToMerge(prevOSIDs => {
                if (prevOSIDs.includes(osID)) {
                    // Uncheck if already checked.
                    return prevOSIDs.filter(prevOSID => prevOSID !== osID);
                }
                // Check if not checked.
                return [...prevOSIDs, osID];
            });
        }
    };

    const handleMergeButtonClick = useMergeButtonClickHandler({
        targetFacilityOSID,
        facilityToMergeOSID,
        facilitiesToMergeData: facilitiesToMerge,
        updateToMergeOSID,
        updateTargetOSID,
        fetchToMergeFacility,
        fetchTargetFacility,
        openMergeModal,
    });

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
                        No facilities matching this search
                    </Typography>
                </div>
            </div>
        );
    }

    const facilitiesCount = get(data, 'count', null);

    const LoginLink = props => <Link to={authLoginFormRoute} {...props} />;
    const RegisterLink = props => (
        <Link to={authRegisterFormRoute} {...props} />
    );

    const progress = facilitiesCount
        ? (get(downloadData, 'results.rows', []).length * 100) / facilitiesCount
        : 0;

    const listHeaderInsetComponent = (
        <Grid
            container
            className={`${classes.listHeaderStyles} results-height-subtract`}
        >
            <Grid container item className={classes.regularButtonsContainer}>
                {downloadingCSV ? (
                    <div className={classes.listHeaderButtonStyles}>
                        <div className={classes.downloadLabelStyles}>
                            Downloading...
                        </div>
                        <LinearProgress
                            variant="determinate"
                            value={progress}
                        />
                    </div>
                ) : (
                    <FeatureFlag
                        flag={ALLOW_LARGE_DOWNLOADS}
                        alternative={
                            <DownloadFacilitiesButton
                                disabled={
                                    facilitiesCount >=
                                    FACILITIES_DOWNLOAD_DEFAULT_LIMIT
                                }
                                setLoginRequiredDialogIsOpen={
                                    setLoginRequiredDialogIsOpen
                                }
                            />
                        }
                    >
                        <DownloadFacilitiesButton
                            allowLargeDownloads
                            setLoginRequiredDialogIsOpen={
                                setLoginRequiredDialogIsOpen
                            }
                        />
                    </FeatureFlag>
                )}
                <CopySearch>
                    <Button
                        variant="outlined"
                        onClick={noop}
                        className={classes.copyLinkButton}
                    >
                        <div className={classes.copyLinkButtonContent}>
                            <CopyLinkIcon />
                            Copy Link
                        </div>
                    </Button>
                </CopySearch>
            </Grid>
            <ShowOnly when={!embed && !user.isAnon && user.is_moderation_mode}>
                <Grid item>
                    <Button
                        className={classes.mergeButton}
                        disabled={facilitiesToMerge.length < 2}
                        onClick={handleMergeButtonClick}
                    >
                        Merge
                    </Button>
                </Grid>
            </ShowOnly>
        </Grid>
    );

    const loadingElement = facilities.length !== facilitiesCount && (
        <>
            <Divider />
            <ListItem className={classes.listItemLoadingPlaceholder}>
                <ListItemText primary="Loading more facilities..." />
            </ListItem>
        </>
    );

    const contributorsCount = number => (
        <>
            {number} {number === 1 ? 'contributor' : 'contributors'}
        </>
    );

    return (
        <>
            {listHeaderInsetComponent}
            <div style={filterSidebarStyles.controlPanelContentStyles}>
                <List component="div">
                    <InfiniteAnyHeight
                        className="infinite-scroll"
                        handleScroll={e => handleScroll(e.scrollTop)}
                        containerHeight={resultListHeight}
                        infiniteLoadBeginEdgeOffset={100}
                        isInfiniteLoading={fetching || isInfiniteLoading}
                        onInfiniteLoad={() => {
                            if (!downloadingCSV) {
                                fetchNextPage();
                            }
                        }}
                        loadingSpinnerDelegate={loadingElement}
                        list={facilities.map(
                            ({
                                properties: {
                                    address,
                                    name,
                                    has_approved_claim: hasApprovedClaim,
                                    os_id: osID,
                                    is_closed: isClosed,
                                    number_of_public_contributors: numberOfPublicContributors,
                                },
                            }) => (
                                <>
                                    <Divider />
                                    <ListItem
                                        key={osID}
                                        className={classes.listItemStyles}
                                    >
                                        <ShowOnly
                                            when={
                                                !embed &&
                                                !user.isAnon &&
                                                user.is_moderation_mode
                                            }
                                        >
                                            <Checkbox
                                                className={
                                                    classes.mergeCheckbox
                                                }
                                                onChange={() =>
                                                    handleCheckboxChange(osID)
                                                }
                                                checked={facilitiesToMerge.includes(
                                                    osID,
                                                )}
                                                disabled={
                                                    facilitiesToMerge.length ===
                                                        2 &&
                                                    !facilitiesToMerge.includes(
                                                        osID,
                                                    )
                                                }
                                            />
                                        </ShowOnly>
                                        <div
                                            className={
                                                classes.facilityLinkWrapper
                                            }
                                        >
                                            <Link
                                                to={{
                                                    pathname: makeFacilityDetailLink(
                                                        osID,
                                                        search,
                                                    ),
                                                    state: {
                                                        panMapToFacilityDetails: true,
                                                    },
                                                }}
                                                href={makeFacilityDetailLink(
                                                    osID,
                                                    search,
                                                )}
                                                className={classes.linkStyles}
                                            >
                                                <span
                                                    style={{
                                                        fontWeight: 700,
                                                        fontSize: '26px',
                                                        letterSpacing:
                                                            '-0.004em',
                                                    }}
                                                >
                                                    {name}
                                                </span>
                                                <Grid
                                                    container
                                                    className={
                                                        classes.facilityDetailContainer
                                                    }
                                                >
                                                    <Grid
                                                        item
                                                        className={
                                                            classes.facilityDetailItem
                                                        }
                                                    >{`OS ID: ${osID}`}</Grid>
                                                    <ShowOnly
                                                        when={
                                                            !embed &&
                                                            numberOfPublicContributors !==
                                                                0
                                                        }
                                                    >
                                                        <Grid
                                                            item
                                                            className={
                                                                classes.facilityDetailItem
                                                            }
                                                        >
                                                            {contributorsCount(
                                                                numberOfPublicContributors,
                                                            )}
                                                        </Grid>
                                                    </ShowOnly>
                                                    <ShowOnly
                                                        when={hasApprovedClaim}
                                                    >
                                                        <Grid
                                                            container
                                                            item
                                                            alignItems="center"
                                                            style={{
                                                                width: 'auto',
                                                            }}
                                                            className={
                                                                classes.facilityDetailItem
                                                            }
                                                        >
                                                            <BadgeClaimed color="#4A9957" />
                                                            <span
                                                                style={{
                                                                    color:
                                                                        '#4A9957',
                                                                    fontWeight: 800,
                                                                }}
                                                            >
                                                                Claimed
                                                            </span>
                                                        </Grid>
                                                    </ShowOnly>
                                                </Grid>
                                                {address}
                                            </Link>
                                            {isClosed ? (
                                                <FeatureFlag
                                                    flag={REPORT_A_FACILITY}
                                                >
                                                    <div
                                                        className={
                                                            classes.closureRibbon
                                                        }
                                                    >
                                                        Closed facility
                                                    </div>
                                                </FeatureFlag>
                                            ) : null}
                                        </div>
                                    </ListItem>
                                </>
                            ),
                        )}
                    />
                </List>
            </div>
            <Dialog open={loginRequiredDialogIsOpen}>
                {loginRequiredDialogIsOpen ? (
                    <>
                        <DialogTitle>Log In To Download</DialogTitle>
                        <DialogContent>
                            <Typography>
                                You must log in with an Open Supply Hub account
                                before downloading your search results.
                            </Typography>
                        </DialogContent>
                        <DialogActions>
                            <Button
                                variant="outlined"
                                color="secondary"
                                onClick={() =>
                                    setLoginRequiredDialogIsOpen(false)
                                }
                            >
                                Cancel
                            </Button>
                            <Button
                                variant="outlined"
                                color="primary"
                                onClick={() =>
                                    setLoginRequiredDialogIsOpen(false)
                                }
                                component={RegisterLink}
                            >
                                Register
                            </Button>
                            <Button
                                variant="outlined"
                                color="primary"
                                onClick={() =>
                                    setLoginRequiredDialogIsOpen(false)
                                }
                                component={LoginLink}
                            >
                                Log In
                            </Button>
                        </DialogActions>
                    </>
                ) : (
                    <div style={{ display: 'none' }} />
                )}
            </Dialog>
        </>
    );
}

FilterSidebarFacilitiesTab.defaultProps = {
    user: {
        isAnon: true,
    },
    data: null,
    error: null,
};

FilterSidebarFacilitiesTab.propTypes = {
    user: userPropType,
    data: facilityCollectionPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
    downloadingCSV: bool.isRequired,
    returnToSearchTab: func.isRequired,
    openMergeModal: func.isRequired,
    fetchNextPage: func.isRequired,
    isInfiniteLoading: bool.isRequired,
    embed: bool.isRequired,
    targetFacilityOSID: string.isRequired,
    facilityToMergeOSID: string.isRequired,
    updateToMergeOSID: func.isRequired,
    fetchToMergeFacility: func.isRequired,
    updateTargetOSID: func.isRequired,
    fetchTargetFacility: func.isRequired,
};

function mapStateToProps({
    auth: {
        user: { user },
    },
    facilities: {
        facilities: { data, error, fetching, isInfiniteLoading },
    },
    mergeFacilities: {
        targetFacility: { osID: targetFacilityOSID },
        facilityToMerge: { osID: facilityToMergeOSID },
    },
    ui: {
        facilitiesSidebarTabSearch: { filterText },
        window: { innerHeight: windowHeight },
        scrollTop,
    },
    logDownload: { fetching: downloadingCSV },
    facilitiesDownload: {
        facilities: { data: downloadData },
    },
    embeddedMap: { embed },
}) {
    return {
        user,
        data,
        downloadData,
        error,
        fetching,
        filterText,
        downloadingCSV,
        windowHeight,
        isInfiniteLoading,
        targetFacilityOSID,
        facilityToMergeOSID,
        scrollTop,
        embed: !!embed,
    };
}

function mapDispatchToProps(dispatch) {
    return {
        returnToSearchTab: () => dispatch(toggleFilterModal()),
        openMergeModal: () => dispatch(toggleMergeModal()),
        fetchNextPage: () => dispatch(fetchNextPageOfFacilities()),
        handleScroll: scrollTop => dispatch(reportListScroll(scrollTop)),
        updateTargetOSID: osID => dispatch(updateMergeTargetFacilityOSID(osID)),
        fetchToMergeFacility: () => dispatch(fetchFacilityToMerge()),
        updateToMergeOSID: osID => dispatch(updateFacilityToMergeOSID(osID)),
        fetchTargetFacility: () => dispatch(fetchMergeTargetFacility()),
    };
}

export default withRouter(
    connect(
        mapStateToProps,
        mapDispatchToProps,
    )(withStyles(makeFacilitiesTabStyles)(FilterSidebarFacilitiesTab)),
);
