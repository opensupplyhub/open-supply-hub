import React, { useState, useEffect } from 'react';
import { connect, useDispatch } from 'react-redux';
import { bool, func, string, object, number } from 'prop-types';
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
    updateAfterDate,
    updateBeforeDate,
} from '../../actions/dashboardModerationQueue';
import { fetchCountryOptions } from '../../actions/filterOptions';
import { moderationEventsPropType } from '../../util/propTypes';
import { makeDashboardModerationQueueStyles } from '../../util/styles';
import { MODERATION_QUEUE } from '../../util/constants';

const DashboardModerationQueue = ({
    events,
    count,
    fetching,
    fetchEvents,
    error,
    downloadEvents,
    downloadEventsError,
    fetchCountries,
    classes,
}) => {
    const [afterDate, setAfterDate] = useState('');
    const [beforeDate, setBeforeDate] = useState('');
    const [afterDateError, setAfterDateError] = useState(false);
    const [beforeDateError, setBeforeDateError] = useState(false);

    const dispatch = useDispatch();

    useEffect(() => {
        fetchEvents();
        fetchCountries();
    }, [fetchEvents, fetchCountries]);

    const handleAfterDateChange = date => {
        if (!beforeDate || date <= beforeDate) {
            setAfterDate(date);
            setAfterDateError(false);
            dispatch(updateAfterDate(date));
        } else {
            setAfterDate('');
            setAfterDateError(true);
        }
    };

    const handleBeforeDateChange = date => {
        if (!afterDate || date >= afterDate) {
            setBeforeDate(date);
            setBeforeDateError(false);
            dispatch(updateBeforeDate(date));
        } else {
            setBeforeDate('');
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
                fetchEvents={fetchEvents}
            />
        </Paper>
    );
};

DashboardModerationQueue.defaultProps = {
    events: [],
    count: 0,
    error: null,
    downloadEventsError: null,
};

DashboardModerationQueue.propTypes = {
    events: moderationEventsPropType,
    count: number,
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
        moderationEvents: { events, count, fetching, error },
        moderationEventsDownloadStatus: { error: downloadEventsError },
    },
}) => ({
    events,
    count,
    fetching,
    error,
    downloadEventsError,
});

const mapDispatchToProps = dispatch => ({
    fetchEvents: (page, pageSize) =>
        dispatch(fetchModerationEvents(page, pageSize)),
    fetchCountries: () => dispatch(fetchCountryOptions()),
    downloadEvents: moderationEvents =>
        dispatch(downloadModerationEvents(moderationEvents)),
});

export default connect(
    mapStateToProps,
    mapDispatchToProps,
)(withStyles(makeDashboardModerationQueueStyles)(DashboardModerationQueue));
