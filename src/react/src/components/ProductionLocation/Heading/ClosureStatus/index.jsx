import React from 'react';
import get from 'lodash/get';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import FeatureFlag from '../../../FeatureFlag';
import { REPORT_A_FACILITY } from '../../../../util/constants';

import getPrimaryText from './utils';
import styles from './styles';

const ProductionLocationDetailClosureStatus = ({
    data,
    clearFacility,
    classes,
    useProductionLocationPage = false,
    search = '',
}) => {
    const report = get(data, 'properties.activity_reports[0]');
    const newOsId = get(data, 'properties.new_os_id');
    const isClosed = get(data, 'properties.is_closed');
    const isPending = report?.status === 'PENDING';

    if (!report) return null;

    if (!isPending && !isClosed) return null;

    const primaryText = getPrimaryText({
        report,
        isPending,
        isClosed,
        newOsId,
        classes,
        useProductionLocationPage,
        search,
        clearFacility,
    });

    return (
        <FeatureFlag flag={REPORT_A_FACILITY}>
            <div className={classes.status}>
                <div className={classes.contentContainer}>
                    <i
                        className={`${classes.text} ${classes.icon} far fa-fw fa-store-slash`}
                    />
                    <div className={classes.textBox}>
                        {primaryText}
                        {isPending && (
                            <Typography
                                className={classes.text}
                                variant="body1"
                            >
                                Status pending
                            </Typography>
                        )}
                    </div>
                </div>
            </div>
        </FeatureFlag>
    );
};

export default withStyles(styles)(ProductionLocationDetailClosureStatus);
