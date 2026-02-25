import React from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import Block from '@material-ui/icons/Block';
import Edit from '@material-ui/icons/Edit';
import FileCopy from '@material-ui/icons/FileCopy';
import Flag from '@material-ui/icons/Flag';
import ChevronRight from '@material-ui/icons/ChevronRight';

import ShowOnly from '../../../ShowOnly';

import {
    makeContributeProductionLocationUpdateURL,
    makeReportADuplicateEmailLink,
    makeDisputeClaimEmailLink,
} from '../../../../util/util';

import useReportStatusDialog from './hooks';
import shouldShowDisputeClaim from './utils';
import ReportFacilityStatusDialog from './ReportFacilityStatusDialog/ReportFacilityStatusDialog';
import productionLocationSidebarContributeFieldsStyles from './styles';

const ProductionLocationDetailsContributeFields = ({
    classes,
    osId,
    showDisputeClaim,
    isClosed,
}) => {
    const [showDialog, openDialog, closeDialog] = useReportStatusDialog();

    return (
        <div
            className={`${classes.contributeSectionContainer} ${classes.container}`}
        >
            <Typography
                variant="title"
                className={classes.title}
                component="h2"
            >
                Contribute to this profile
            </Typography>
            <Typography variant="body1" className={classes.subtitle}>
                Help improve supply chain transparency
            </Typography>
            <Grid container spacing={0} className={classes.actionsList}>
                <Grid item className={classes.actionItemWrapper}>
                    <Link
                        to={makeContributeProductionLocationUpdateURL(osId)}
                        target="_blank"
                        rel="noreferrer"
                        className={classes.actionItem}
                    >
                        <Flag className={classes.actionIcon} />
                        <Typography
                            variant="body1"
                            className={classes.actionLabel}
                        >
                            Suggest Correction
                        </Typography>
                        <ChevronRight className={classes.actionChevron} />
                    </Link>
                </Grid>
                <Grid item className={classes.actionItemWrapper}>
                    <Link
                        to={makeReportADuplicateEmailLink(osId)}
                        target="_blank"
                        rel="noreferrer"
                        className={classes.actionItem}
                    >
                        <FileCopy className={classes.actionIcon} />
                        <Typography
                            variant="body1"
                            className={classes.actionLabel}
                        >
                            Report Duplicate
                        </Typography>
                        <ChevronRight className={classes.actionChevron} />
                    </Link>
                </Grid>
                <ShowOnly when={showDisputeClaim}>
                    <Grid item className={classes.actionItemWrapper}>
                        <Link
                            to={makeDisputeClaimEmailLink(osId)}
                            target="_blank"
                            rel="noreferrer"
                            className={classes.actionItem}
                        >
                            <Edit className={classes.actionIcon} />
                            <Typography
                                variant="body1"
                                className={classes.actionLabel}
                            >
                                Dispute Claim
                            </Typography>
                            <ChevronRight className={classes.actionChevron} />
                        </Link>
                    </Grid>
                </ShowOnly>
                <Grid item className={classes.actionItemWrapper}>
                    <div
                        role="button"
                        tabIndex={0}
                        onClick={openDialog}
                        onKeyDown={e => e.key === 'Enter' && openDialog()}
                        className={classes.actionItem}
                    >
                        <Block className={classes.actionIcon} />
                        <Typography
                            variant="body1"
                            className={classes.actionLabel}
                        >
                            {isClosed ? 'Report Reopened' : 'Report Closed'}
                        </Typography>
                        <ChevronRight className={classes.actionChevron} />
                    </div>
                </Grid>
            </Grid>
            <ReportFacilityStatusDialog
                open={showDialog}
                onClose={closeDialog}
            />
        </div>
    );
};

const mapStateToProps = (
    {
        facilities: {
            singleFacility: { data },
        },
        auth: { user },
    },
    { osId },
) => ({
    showDisputeClaim: shouldShowDisputeClaim(data, osId, user),
    isClosed: data?.properties?.is_closed,
});

export default connect(mapStateToProps)(
    withStyles(productionLocationSidebarContributeFieldsStyles)(
        ProductionLocationDetailsContributeFields,
    ),
);
