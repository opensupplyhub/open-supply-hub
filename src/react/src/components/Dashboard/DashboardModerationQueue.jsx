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
import { moderationEventsPropType } from '../../util/propTypes';
import { makeDashboardModerationQueueStyles } from '../../util/styles';
import {
    MODERATION_QUEUE,
    MODERATION_INITIAL_PAGE_INDEX,
    MODERATION_DEFAULT_ROWS_PER_PAGE,
} from '../../util/constants';

const DashboardModerationQueue = ({
    events,
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
    fetchEvents,
    error,
    downloadEvents,
    downloadEventsError,
    fetchCountries,
    classes,
}) => {
    const [afterDateError, setAfterDateError] = useState(false);
    const [beforeDateError, setBeforeDateError] = useState(false);
    const isFirstRender = useRef(true);
    const prevDataSources = useRef(dataSources);
    const prevModerationStatuses = useRef(moderationStatuses);
    const prevCountries = useRef(countries);

    const dispatch = useDispatch();

    useEffect(() => {
        fetchEvents();
        fetchCountries();
    }, [fetchEvents, fetchCountries]);

    const wasNotEmptyAndNowEmpty = (prev, current) =>
        prev?.current?.length > 0 && current?.length === 0;

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
            fetchEvents();
        }

        prevDataSources.current = dataSources;
        prevModerationStatuses.current = moderationStatuses;
        prevCountries.current = countries;
    }, [dataSources, moderationStatuses, countries]);

    const handleAfterDateChange = date => {
        if (!beforeDate || !date || date <= beforeDate) {
            setAfterDateError(false);
            dispatch(updateAfterDate(date));
            dispatch(clearModerationEvents());
            dispatch(
                updateModerationEventsPage({
                    page: MODERATION_INITIAL_PAGE_INDEX,
                    maxPage: MODERATION_INITIAL_PAGE_INDEX,
                    pageSize,
                }),
            );
            fetchEvents();
        } else {
            dispatch(updateAfterDate(''));
            setAfterDateError(true);
        }
    };

    const handleBeforeDateChange = date => {
        if (!afterDate || !date || date >= afterDate) {
            setBeforeDateError(false);
            dispatch(updateBeforeDate(date));
            dispatch(clearModerationEvents());
            dispatch(
                updateModerationEventsPage({
                    page: MODERATION_INITIAL_PAGE_INDEX,
                    maxPage: MODERATION_INITIAL_PAGE_INDEX,
                    pageSize,
                }),
            );
            fetchEvents();
        } else {
            dispatch(updateBeforeDate(''));
            setBeforeDateError(true);
        }
    };

    if (error) {
        return <Typography>{error}</Typography>;
    }

    const eventsCount = count;

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
                    downloadPayload={events || []}
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
                        The &apos;After Date&apos; should be earlier than or the
                        same as the &apos;Before Date&apos;. Please adjust the
                        dates.
                    </Typography>
                )}
            </div>

            <Grid item className={classes.numberResults}>
                {eventsCount} results
            </Grid>

            <DashboardModerationQueueListTable
                fetching={fetching}
                events={events}
                count={count}
                page={page}
                maxPage={maxPage}
                pageSize={pageSize}
                sort={sort}
                fetchEvents={fetchEvents}
            />
        </Paper>
    );
};

DashboardModerationQueue.defaultProps = {
    events: [],
    count: 0,
    page: MODERATION_INITIAL_PAGE_INDEX,
    maxPage: MODERATION_INITIAL_PAGE_INDEX,
    pageSize: MODERATION_DEFAULT_ROWS_PER_PAGE,
    sort: {
        sortBy: 'created_at',
        orderBy: 'desc',
    },
    afterDate: null,
    beforeDate: null,
    dataSources: [],
    moderationStatuses: [],
    countries: [],
    error: null,
    downloadEventsError: null,
};

DashboardModerationQueue.propTypes = {
    events: moderationEventsPropType,
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
    fetchEvents: func.isRequired,
    fetchCountries: func.isRequired,
    downloadEvents: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    dashboardModerationQueue: {
        moderationEvents: {
            events,
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
    events,
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
    fetchEvents: () => dispatch(fetchModerationEvents()),
    fetchCountries: () => dispatch(fetchCountryOptions()),
    downloadEvents: moderationEvents =>
        dispatch(downloadModerationEvents(moderationEvents)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(makeDashboardModerationQueueStyles)(DashboardModerationQueue));
