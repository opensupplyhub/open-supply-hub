import React from 'react';
import { object, oneOfType, string, instanceOf } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import ScheduleIcon from '@material-ui/icons/Schedule';

import { DATE_FORMATS } from '../../../../util/constants';
import { formatDate } from '../../../../util/util';
import contributionDateStyles from './styles';

const ContributionDate = ({ classes, date }) => (
    <span className={classes.dateWithIcon} data-testid="contribution-date">
        <ScheduleIcon fontSize="small" className={classes.dateIcon} />
        {formatDate(date, DATE_FORMATS.LONG)}
    </span>
);

ContributionDate.propTypes = {
    classes: object.isRequired,
    date: oneOfType([string, instanceOf(Date)]).isRequired,
};

export default withStyles(contributionDateStyles)(ContributionDate);
