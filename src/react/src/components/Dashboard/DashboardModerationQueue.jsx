import React, { useState, useEffect } from 'react';
import { connect } from 'react-redux';
import { arrayOf, bool, func, string, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import CountryNameFilter from '../Filters/CountryNameFilter';
import SourceTypeFilter from '../Filters/SourceTypeFilter';
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
    downloadError,
    fetchCountries,
    classes,
}) => {
    const [afterDate, setAfterDate] = useState('');
    const [beforeDate, setBeforeDate] = useState('');

    useEffect(() => {
        fetchEvents();
        fetchCountries();
    }, [fetchEvents, fetchCountries]);

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
                    downloadError={downloadError}
                />
                <SourceTypeFilter
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
                            onChange={setAfterDate}
                            name="after-date"
                        />
                    </Grid>
                    <Grid item>
                        <DatePicker
                            label="Before Date:"
                            value={beforeDate}
                            onChange={setBeforeDate}
                            name="before-date"
                        />
                    </Grid>
                </Grid>
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
    events: null,
    error: null,
    downloadError: null,
};

DashboardModerationQueue.propTypes = {
    events: moderationEventsPropType,
    fetching: bool.isRequired,
    error: arrayOf(string),
    downloadError: arrayOf(string),
    fetchEvents: func.isRequired,
    fetchCountries: func.isRequired,
    downloadEvents: func.isRequired,
    classes: object.isRequired,
};

const mapStateToProps = ({
    dashboardModerationQueue: {
        moderationEvents: { events, fetching, error },
        moderationEventsDownloadStatus: { error: downloadError },
    },
}) => ({
    events,
    fetching,
    error,
    downloadError,
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
