import React from 'react';
import get from 'lodash/get';
import Typography from '@material-ui/core/Typography';
import { withStyles } from '@material-ui/core/styles';

import FeatureFlag from '../../../FeatureFlag';
import { REPORT_A_FACILITY } from '../../../../util/constants';

import PrimaryText from './PrimaryText';
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

    return (
        <FeatureFlag flag={REPORT_A_FACILITY}>
            <div className={classes.status}>
                <div className={classes.contentContainer}>
                    <div className={classes.iconColumn}>
                        <i
                            className={`${classes.text} ${classes.icon} far fa-fw fa-store-slash`}
                        />
                    </div>
                    <div className={classes.textBox}>
                        <PrimaryText
                            report={report}
                            isPending={isPending}
                            isClosed={isClosed}
                            newOsId={newOsId}
                            classes={classes}
                            useProductionLocationPage={
                                useProductionLocationPage
                            }
                            search={search}
                            clearFacility={clearFacility}
                        />
                        {isPending && (
                            <Typography
                                className={`${classes.text} ${classes.statusPending}`}
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
