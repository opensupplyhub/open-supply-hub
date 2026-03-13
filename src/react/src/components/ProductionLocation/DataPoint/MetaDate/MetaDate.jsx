import React from 'react';
import { object, oneOfType, string, instanceOf } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';
import ScheduleIcon from '@material-ui/icons/Schedule';

import { DATE_FORMATS } from '../../../../util/constants';
import { formatDate } from '../../../../util/util';
import metaDateStyles from './styles';

const MetaDate = ({ classes, date }) => (
    <span className={classes.root} data-testid="data-point-date">
        <ScheduleIcon fontSize="small" className={classes.icon} />
        <Typography variant="body2" component="span" className={classes.text}>
            {formatDate(date, DATE_FORMATS.LONG)}
        </Typography>
    </span>
);

MetaDate.propTypes = {
    classes: object.isRequired,
    date: oneOfType([string, instanceOf(Date)]).isRequired,
};

export default withStyles(metaDateStyles)(MetaDate);
