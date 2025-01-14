import React, { useState, useEffect, useRef } from 'react';
import { connect, useDispatch } from 'react-redux';
import { bool, func, string, object, number, array } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import CountryNameFilter from '../Filters/CountryNameFilter';
import DataSourceFilter from '../Filters/DataSourceFilter';
import ModerationStatusFilter from '../Filters/ModerationStatusFilter';
import DashboardModerationQueueListTable from './DashboardModerationQueueListTable';
import DashboardDownloadDataButton from './DashboardDownloadDataButton';
import DatePicker from '../DatePicker';
import {
    fetchModerationEvents,
    downloadModerationEvents,
    clearModerationEvents,
    updateModerationEventsPage,
    updateAfterDate,
    updateBeforeDate,
} from '../../actions/dashboardModerationQueue';
import { fetchCountryOptions } from '../../actions/filterOptions';
import { moderationEventsListPropType } from '../../util/propTypes';
import { makeDashboardModerationQueueStyles } from '../../util/styles';
import {
    MODERATION_QUEUE,
    MODERATION_INITIAL_PAGE_INDEX,
    MODERATION_DEFAULT_ROWS_PER_PAGE,
} from '../../util/constants';

const DATE_RANGE_ERROR =
    "The 'After Date' should be earlier than or the same as " +
    "the 'Before Date'. Please adjust the dates.";

const DATE_FORMAT_ERROR =
    "The date format is invalid. Please use the format 'DD-MM-YYYY'.";

const DashboardModerationQueue = ({
    moderationEventsList,
    count,
    page,
    maxPage,
    pageSize,
    sort,
    afterDate,
    beforeDate,
    dataSources,
    moderationStatuses,
    countries,
    fetching,
    handleFetchModerationEvents,
    error,
    downloadEvents,
    downloadEventsError,
    fetchCountries,
    classes,
}) => {
    const [afterDateError, setAfterDateError] = useState(false);
    const [beforeDateError, setBeforeDateError] = useState(false);
    const [errorDateText, setErrorDateText] = useState('');
    const isFirstRender = useRef(true);
    const prevDataSources = useRef(dataSources);
    const prevModerationStatuses = useRef(moderationStatuses);
    const prevCountries = useRef(countries);

    const dispatch = useDispatch();

    const dateRegexFormat = /^\d{4}-\d{2}-\d{2}$/;

    useEffect(() => {
        handleFetchModerationEvents();
        fetchCountries();
    }, [handleFetchModerationEvents, fetchCountries]);

    const wasNotEmptyAndNowEmpty = (prev, current) =>
        prev?.current?.length > 0 && current?.length === 0;

    const isValidDate = date =>
        typeof date === 'string' &&
        (date.length === 0 || dateRegexFormat.test(date));
    const isValidDateRange = (firstDate, secondDate) =>
        firstDate.length === 0 ||
        secondDate.length === 0 ||
        firstDate >= secondDate;

    useEffect(() => {
        /*
         Fetch data if prev filters were not empty but
         become empty after user click on select field.
         This will resolve conflict of when we want to fetch data
         when filters are removing in UI at the moment
        */
        const wasNotEmptyAndNowEmptyDataSources = wasNotEmptyAndNowEmpty(
            prevDataSources,
            dataSources,
        );
        const wasNotEmptyAndNowEmptyModerationStatuses = wasNotEmptyAndNowEmpty(
            prevModerationStatuses,
            moderationStatuses,
        );
        const wasNotEmptyAndNowEmptyCountries = wasNotEmptyAndNowEmpty(
            prevCountries,
            countries,
        );

        if (isFirstRender.current) {
            isFirstRender.current = false;
        } else if (
            dataSources.length > 0 ||
            wasNotEmptyAndNowEmptyDataSources ||
            moderationStatuses.length > 0 ||
            wasNotEmptyAndNowEmptyModerationStatuses ||
            countries.length > 0 ||
            wasNotEmptyAndNowEmptyCountries
        ) {
            dispatch(clearModerationEvents());
            dispatch(
                updateModerationEventsPage({
                    page: MODERATION_INITIAL_PAGE_INDEX,
                    maxPage: MODERATION_INITIAL_PAGE_INDEX,
                    pageSize,
                }),
            );
            handleFetchModerationEvents();
        }

        prevDataSources.current = dataSources;
        prevModerationStatuses.current = moderationStatuses;
        prevCountries.current = countries;
    }, [dataSources, moderationStatuses, countries]);

    const handleAfterDateChange = date => {
        setAfterDateError(false);
        setBeforeDateError(false);
        if (!isValidDate(date)) {
            dispatch(updateAfterDate(null));
            setErrorDateText(DATE_FORMAT_ERROR);
            setAfterDateError(true);
            return;
        }
        if (!isValidDateRange(beforeDate, date)) {
            dispatch(updateAfterDate(date));
            setErrorDateText(DATE_RANGE_ERROR);
            setAfterDateError(true);
            return;
        }

        dispatch(updateAfterDate(date));
        dispatch(clearModerationEvents());
        dispatch(
            updateModerationEventsPage({
                page: MODERATION_INITIAL_PAGE_INDEX,
                maxPage: MODERATION_INITIAL_PAGE_INDEX,
                pageSize,
            }),
        );
        handleFetchModerationEvents();
    };

    const handleBeforeDateChange = date => {
        setAfterDateError(false);
        setBeforeDateError(false);
        if (!isValidDate(date)) {
            dispatch(updateBeforeDate(null));
            setErrorDateText(DATE_FORMAT_ERROR);
            setBeforeDateError(true);
            return;
        }
        if (!isValidDateRange(date, afterDate)) {
            dispatch(updateBeforeDate(date));
            setErrorDateText(DATE_RANGE_ERROR);
            setBeforeDateError(true);
            return;
        }

        dispatch(updateBeforeDate(date));
        dispatch(clearModerationEvents());
        dispatch(
            updateModerationEventsPage({
                page: MODERATION_INITIAL_PAGE_INDEX,
                maxPage: MODERATION_INITIAL_PAGE_INDEX,
                pageSize,
            }),
        );
        handleFetchModerationEvents();
    };

    if (error) {
        return <Typography>{error}</Typography>;
    }

    const moderationEventsCount = count;

    const sharedFilterProps = {
        isDisabled: fetching,
        className: 'form__field--dense',
        origin: MODERATION_QUEUE,
    };

    return (
        <Paper className={classes.mainContainer}>
            <div className={classes.dashboardFilters}>
                <DashboardDownloadDataButton
                    fetching={fetching}
                    downloadPayload={moderationEventsList || []}
                    downloadData={downloadEvents}
                    downloadError={downloadEventsError}
                />
                <DataSourceFilter {...sharedFilterProps} />
                <ModerationStatusFilter {...sharedFilterProps} />
                <CountryNameFilter {...sharedFilterProps} />
                <Grid
                    container
                    className={classes.datePickersContainer}
                    spacing={16}
                    alignItems="center"
                >
                    <Grid item>
                        <DatePicker
                            label="After Date:"
                            value={afterDate}
                            onChange={handleAfterDateChange}
                            name="after-date"
                            error={afterDateError}
                        />
                    </Grid>
                    <Grid item>
                        <DatePicker
                            label="Before Date:"
                            value={beforeDate}
                            onChange={handleBeforeDateChange}
                            name="before-date"
                            error={beforeDateError}
                        />
                    </Grid>
                </Grid>
                {(afterDateError || beforeDateError) && (
                    <Typography color="error" className={classes.errorText}>
                        {errorDateText}
                    </Typography>
                )}
            </div>

            <Grid item className={classes.numberResults}>
                {moderationEventsCount} results
            </Grid>

            <DashboardModerationQueueListTable
                fetching={fetching}
                moderationEventsList={moderationEventsList}
                count={count}
                page={page}
                maxPage={maxPage}
                pageSize={pageSize}
                sort={sort}
                fetchModerationEvents={handleFetchModerationEvents}
            />
        </Paper>
    );
};

DashboardModerationQueue.defaultProps = {
    moderationEventsList: [],
    count: 0,
    page: MODERATION_INITIAL_PAGE_INDEX,
    maxPage: MODERATION_INITIAL_PAGE_INDEX,
    pageSize: MODERATION_DEFAULT_ROWS_PER_PAGE,
    sort: {
        sortBy: 'created_at',
        orderBy: 'desc',
    },
    afterDate: '',
    beforeDate: '',
    dataSources: [],
    moderationStatuses: [],
    countries: [],
    error: null,
    downloadEventsError: null,
};

DashboardModerationQueue.propTypes = {
    moderationEventsList: moderationEventsListPropType,
    count: number,
    page: number,
    maxPage: number,
    pageSize: number,
    sort: object,
    afterDate: string,
    beforeDate: string,
    dataSources: array,
    moderationStatuses: array,
    countries: array,
    fetching: bool.isRequired,
    error: string,
    downloadEventsError: string,
    handleFetchModerationEvents: func.isRequired,
    fetchCountries: func.isRequired,
    downloadEvents: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    dashboardModerationQueue: {
        moderationEvents: {
            moderationEventsList,
            count,
            page,
            maxPage,
            pageSize,
            sort,
            afterDate,
            beforeDate,
            fetching,
            error,
        },
        moderationEventsDownloadStatus: { error: downloadEventsError },
    },
    filters: { dataSources, moderationStatuses, countries },
}) => ({
    moderationEventsList,
    count,
    page,
    maxPage,
    pageSize,
    sort,
    afterDate,
    beforeDate,
    dataSources,
    moderationStatuses,
    countries,
    fetching,
    error,
    downloadEventsError,
});

const mapDispatchToProps = dispatch => ({
    handleFetchModerationEvents: () => dispatch(fetchModerationEvents()),
    fetchCountries: () => dispatch(fetchCountryOptions()),
    downloadEvents: moderationEvents =>
        dispatch(downloadModerationEvents(moderationEvents)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(makeDashboardModerationQueueStyles)(DashboardModerationQueue));
