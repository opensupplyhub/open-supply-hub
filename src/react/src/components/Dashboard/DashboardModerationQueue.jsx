import React, { useState, useEffect } from 'react';
import { connect } from 'react-redux';
import { bool, func, string, object } from 'prop-types';
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
} from '../../actions/dashboardModerationQueue';
import { fetchCountryOptions } from '../../actions/filterOptions';
import { moderationEventsPropType } from '../../util/propTypes';
import { makeDashboardModerationQueueStyles } from '../../util/styles';

const DashboardModerationQueue = ({
    events,
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

    useEffect(() => {
        fetchEvents();
        fetchCountries();
    }, [fetchEvents, fetchCountries]);

    const handleAfterDateChange = date => {
        if (!beforeDate || date <= beforeDate) {
            setAfterDate(date);
            setAfterDateError(false);
        } else {
            setAfterDate('');
            setAfterDateError(true);
        }
    };

    const handleBeforeDateChange = date => {
        if (!afterDate || date >= afterDate) {
            setBeforeDate(date);
            setBeforeDateError(false);
        } else {
            setBeforeDate('');
            setBeforeDateError(true);
        }
    };

    if (error) {
        return <Typography>{error}</Typography>;
    }

    const eventsCount = events?.length || 0;

    return (
        <Paper className={classes.mainContainer}>
            <div className={classes.dashboardFilters}>
                <DashboardDownloadDataButton
                    fetching={fetching}
                    downloadPayload={events || []}
                    downloadData={downloadEvents}
                    downloadError={downloadEventsError}
                />
                <DataSourceFilter
                    isDisabled={fetching}
                    className="form__field--dense"
                />
                <ModerationStatusFilter
                    isDisabled={fetching}
                    className="form__field--dense"
                />
                <CountryNameFilter
                    isDisabled={fetching}
                    className="form__field--dense"
                />
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
            />
        </Paper>
    );
};

DashboardModerationQueue.defaultProps = {
    events: [],
    error: null,
    downloadEventsError: null,
};

DashboardModerationQueue.propTypes = {
    events: moderationEventsPropType,
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
        moderationEvents: { events, fetching, error },
        moderationEventsDownloadStatus: { error: downloadEventsError },
    },
}) => ({
    events,
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
