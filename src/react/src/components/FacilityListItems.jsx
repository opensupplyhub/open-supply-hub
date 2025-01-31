import React, { useEffect } from 'react';
import { arrayOf, bool, func, string } from 'prop-types';
import { connect } from 'react-redux';
import { Link, Route, useHistory } from 'react-router-dom';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Grid from '@material-ui/core/Grid';
import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import DialogContent from '@material-ui/core/DialogContent';
import DialogActions from '@material-ui/core/DialogActions';
import Check from '@material-ui/icons/Check';

import AppGrid from './AppGrid';
import AppOverflow from './AppOverflow';
import FacilityListItemsEmpty from './FacilityListItemsEmpty';
import FacilityListItemsTable from './FacilityListItemsTable';
import FacilityListControls from './FacilityListControls';
import ListUploadErrors from './ListUploadErrors';

import {
    createPaginationOptionsFromQueryString,
    createParamsFromQueryString,
    replaceListParsingErrorMessages,
} from '../util/util';
import COLOURS from '../util/COLOURS';
import {
    fetchFacilityList,
    fetchFacilityListItems,
    resetFacilityListItems,
    assembleAndDownloadFacilityListCSV,
} from '../actions/facilityListDetails';
import {
    mainRoute,
    OARFont,
    listsRoute,
    facilityListItemsRoute,
    facilityListItemStatusChoicesEnum,
    authLoginFormRoute,
    dashboardListsRoute,
    matchResponsibilityEnum,
} from '../util/constants';
import { facilityListPropType } from '../util/propTypes';

const facilityListItemsStyles = Object.freeze({
    headerStyles: Object.freeze({
        display: 'flex',
        justifyContent: 'space-between',
        padding: '0.5rem',
        marginBottom: '0.5rem',
        marginTop: '60px',
        alignContent: 'center',
        alignItems: 'center',
    }),
    titleStyles: Object.freeze({
        overflowWrap: 'anywhere',
    }),
    subheadStyles: Object.freeze({
        padding: '0.5rem',
        textAlign: 'left',
    }),
    tableStyles: Object.freeze({
        minWidth: '85%',
        width: '90%',
    }),
    tableTitleStyles: Object.freeze({
        fontFamily: OARFont,
        fontWeight: 'normal',
        fontSize: '32px',
    }),
    descriptionStyles: Object.freeze({
        marginBottm: '30px',
    }),
    buttonStyles: Object.freeze({
        marginLeft: '20px',
    }),
    buttonGroupStyles: Object.freeze({
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
    }),
    buttonGroupWithErrorStyles: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignContent: 'center',
    }),
    buttonLinkStyles: Object.freeze({
        marginLeft: '20px',
        padding: '8px 16px',
        border: '1px solid rgba(0, 0, 0, 0.23)',
        textTransform: 'uppercase',
        color: 'rgba(0, 0, 0, 0.87)',
        textDecoration: 'none',
        fontSize: '0.875rem',
        fontWeight: '500',
    }),
});

const refreshListModalStyles = Object.freeze({
    titleContentStyle: Object.freeze({
        textAlign: 'center',
    }),
    icon: Object.freeze({
        color: COLOURS.DARK_GREEN,
        verticalAlign: 'middle',
        marginRight: '10px',
    }),
    separator: Object.freeze({
        color: COLOURS.GREY,
    }),
    dialogContentStyles: Object.freeze({
        textAlign: 'center',
        fontSize: '20px',
    }),
    buttonContentStyle: Object.freeze({
        justifyContent: 'center',
    }),
});

const FacilityListItems = ({
    list,
    fetchingList,
    error,
    downloadingCSV,
    downloadCSV,
    csvDownloadingError,
    userHasSignedIn,
    isAdminUser,
    readOnly,
    fetchList,
    fetchListItems,
    clearListItems,
    adminSearch,
    isListOwner,
    listParsingErrorsExist,
}) => {
    const history = useHistory();

    useEffect(() => {
        fetchList();
        fetchListItems();
        return () => clearListItems();
    }, [fetchList, fetchListItems, clearListItems]);

    if (fetchingList) {
        return (
            <AppGrid title="">
                <CircularProgress />
            </AppGrid>
        );
    }

    if (error && error.length) {
        if (!userHasSignedIn) {
            return (
                <AppGrid title="Unable to retrieve that list">
                    <Link to={authLoginFormRoute}>
                        Sign in to view your Open Supply Hub lists
                    </Link>
                </AppGrid>
            );
        }

        return (
            <AppGrid title="Unable to retrieve that list">
                <ul>
                    {error.map(err => (
                        <li key={err}>{err}</li>
                    ))}
                </ul>
            </AppGrid>
        );
    }

    if (!list) {
        return (
            <AppGrid title="No list was found for that ID">
                <div />
            </AppGrid>
        );
    }

    const csvDownloadErrorMessage = csvDownloadingError &&
        csvDownloadingError.length && (
            <p style={{ color: 'red', textAlign: 'right' }}>
                An error prevented downloading the CSV.
            </p>
        );

    const awaitingModerationMessage = readOnly && (
        <p style={{ color: 'red' }}>
            This list has matches awaiting moderation from the{' '}
            {isAdminUser ? 'contributor' : 'OS Hub admins'}.
        </p>
    );

    const csvDownloadButton = downloadingCSV ? (
        <div>
            <CircularProgress size={25} />
        </div>
    ) : (
        <Button
            variant="outlined"
            color="primary"
            style={facilityListItemsStyles.buttonStyles}
            onClick={downloadCSV}
            disabled={downloadingCSV}
        >
            Download Formatted File
        </Button>
    );

    const originalCsvDownloadButton = list.file && (
        <a
            style={facilityListItemsStyles.buttonLinkStyles}
            href={list.file}
            target="_blank"
            rel="noreferrer"
        >
            Download Submitted File
        </a>
    );

    const backRoute = isAdminUser
        ? `${dashboardListsRoute}${adminSearch || ''}`
        : listsRoute;

    const handleGoToMainPage = () => history.push(mainRoute);

    const listHeader = (
        <>
            <div style={facilityListItemsStyles.headerStyles}>
                <div>
                    <h2 style={facilityListItemsStyles.titleStyles}>
                        {list.name || list.id}
                    </h2>
                    <Typography
                        variant="subheading"
                        style={facilityListItemsStyles.descriptionStyles}
                    >
                        {list.description || ''}
                    </Typography>
                </div>
                <div style={facilityListItemsStyles.buttonGroupWithErrorStyles}>
                    {csvDownloadErrorMessage}
                    <div style={facilityListItemsStyles.buttonGroupStyles}>
                        {csvDownloadButton}
                        {originalCsvDownloadButton}
                        <Button
                            variant="outlined"
                            component={Link}
                            to={backRoute}
                            style={facilityListItemsStyles.buttonStyles}
                        >
                            Back to lists
                        </Button>
                    </div>
                </div>
            </div>

            {(list.item_count > 0 || listParsingErrorsExist) &&
                list.status_counts.UPLOADED === 0 && (
                    <FacilityListControls
                        isAdminUser={isAdminUser}
                        id={list.id}
                    />
                )}
        </>
    );

    const renderListParsingErrors = () => {
        const extractedErrorMessages = replaceListParsingErrorMessages(
            list.parsing_errors,
        );

        return (
            <Grid item style={facilityListItemsStyles.tableStyles}>
                {listHeader}
                <Grid item style={facilityListItemsStyles.tableStyles}>
                    <Typography
                        variant="subheading"
                        style={facilityListItemsStyles.descriptionStyles}
                    >
                        Errors occurred while parsing your list, blocking
                        further processing:
                    </Typography>
                    <ListUploadErrors errors={extractedErrorMessages} />
                </Grid>
            </Grid>
        );
    };

    const renderDialog = () => (
        <Dialog open>
            <DialogTitle style={refreshListModalStyles.titleContentStyle}>
                <Check style={refreshListModalStyles.icon} />
                {isListOwner && 'Thank you for submitting your list!'}
            </DialogTitle>
            <DialogContent>
                <Typography
                    variant="body1"
                    style={refreshListModalStyles.dialogContentStyles}
                >
                    {isListOwner ? 'Your data' : 'Data'} has been successfully
                    uploaded and is being processed.
                    <br />
                    Check back in a few minutes to review the status.
                </Typography>
                <hr style={refreshListModalStyles.separator} />
            </DialogContent>
            <DialogActions style={refreshListModalStyles.buttonContentStyle}>
                <Button
                    variant="outlined"
                    color="secondary"
                    onClick={handleGoToMainPage}
                >
                    Go to the main page
                </Button>
                <Button
                    variant="outlined"
                    color="primary"
                    onClick={() => {
                        window.location.reload();
                    }}
                >
                    Refresh
                </Button>
            </DialogActions>
        </Dialog>
    );

    const renderFacilityList = () => (
        <Grid item style={facilityListItemsStyles.tableStyles}>
            {listHeader}

            <div style={facilityListItemsStyles.subheadStyles}>
                The processing time may be longer for lists that include
                additional data points beyond facility name and address. You
                will receive an email when your list has finished processing.
                {awaitingModerationMessage}
            </div>

            {list.item_count ? (
                <Route
                    path={facilityListItemsRoute}
                    component={FacilityListItemsTable}
                />
            ) : (
                <FacilityListItemsEmpty />
            )}
        </Grid>
    );

    const content = listParsingErrorsExist ? (
        renderListParsingErrors()
    ) : (
        <>
            {!list.item_count && renderDialog()}
            {renderFacilityList()}
        </>
    );

    return (
        <AppOverflow>
            <Grid container justify="center">
                {content}
            </Grid>
        </AppOverflow>
    );
};

FacilityListItems.defaultProps = {
    list: null,
    error: null,
    csvDownloadingError: null,
    adminSearch: null,
    isAdminUser: false,
};

FacilityListItems.propTypes = {
    list: facilityListPropType,
    fetchingList: bool.isRequired,
    error: arrayOf(string),
    fetchList: func.isRequired,
    fetchListItems: func.isRequired,
    clearListItems: func.isRequired,
    downloadCSV: func.isRequired,
    downloadingCSV: bool.isRequired,
    csvDownloadingError: arrayOf(string),
    userHasSignedIn: bool.isRequired,
    isAdminUser: bool,
    readOnly: bool.isRequired,
    adminSearch: string,
    isListOwner: bool.isRequired,
    listParsingErrorsExist: bool.isRequired,
};

const mapStateToProps = ({
    facilityListDetails: {
        list: { data: list, fetching: fetchingList, error: listError },
        items: { data: items, error: itemsError },
        downloadCSV: { fetching: downloadingCSV, error: csvDownloadingError },
    },
    auth: {
        user: { user },
    },
}) => {
    const isAdminUser =
        !user.isAnon &&
        user.is_superuser &&
        list &&
        user.contributor_id !== list.contributor_id;
    const hasPendingItems =
        !!items &&
        items.some(
            item =>
                item.status ===
                facilityListItemStatusChoicesEnum.POTENTIAL_MATCH,
        );
    const readOnly =
        !!list &&
        hasPendingItems &&
        ((list.match_responsibility === matchResponsibilityEnum.CONTRIBUTOR &&
            isAdminUser) ||
            (list.match_responsibility === matchResponsibilityEnum.MODERATOR &&
                !isAdminUser));

    const isListOwner =
        !user.isAnon && !!list && user.contributor_id === list.contributor_id;

    const listParsingErrorsExist =
        !!list && list.parsing_errors && list.parsing_errors.length > 0;

    return {
        list,
        fetchingList,
        error: listError || itemsError,
        downloadingCSV,
        csvDownloadingError,
        userHasSignedIn: !user.isAnon,
        isAdminUser,
        readOnly,
        isListOwner,
        listParsingErrorsExist,
    };
};

const mapDispatchToProps = (
    dispatch,
    {
        match: {
            params: { listID },
        },
        history: {
            location: { search, state: { search: adminSearch } = {} },
        },
    },
) => {
    const { page, rowsPerPage } = createPaginationOptionsFromQueryString(
        search,
    );
    const params = createParamsFromQueryString(search);

    return {
        fetchList: () => dispatch(fetchFacilityList(listID)),
        fetchListItems: () =>
            dispatch(fetchFacilityListItems(listID, page, rowsPerPage, params)),
        clearListItems: () => dispatch(resetFacilityListItems()),
        downloadCSV: () => dispatch(assembleAndDownloadFacilityListCSV()),
        adminSearch,
    };
};

export default connect(mapStateToProps, mapDispatchToProps)(FacilityListItems);
