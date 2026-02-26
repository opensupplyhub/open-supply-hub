import React from 'react';
import { Link } from 'react-router-dom';
import { connect } from 'react-redux';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';

import Add from '@material-ui/icons/Add';
import CheckCircleOutline from '@material-ui/icons/CheckCircleOutline';
import HighlightOff from '@material-ui/icons/HighlightOff';

import { ReactComponent as CopyIcon } from './icons/copy.svg';
import { ReactComponent as ShieldXIcon } from './icons/shield-x.svg';

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
            data-testid="contribute-fields"
        >
            <Typography
                variant="title"
                className={classes.title}
                component="h3"
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
                        data-testid="contribute-suggest-correction"
                    >
                        <Add className={classes.actionIcon} />
                        <Typography
                            variant="body1"
                            className={classes.actionLabel}
                        >
                            Suggest Correction
                        </Typography>
                    </Link>
                </Grid>
                <Grid item className={classes.actionItemWrapper}>
                    <a
                        href={makeReportADuplicateEmailLink(osId)}
                        className={classes.actionItem}
                        data-testid="contribute-report-duplicate"
                    >
                        <CopyIcon className={classes.actionIcon} />
                        <Typography
                            variant="body1"
                            className={classes.actionLabel}
                        >
                            Report Duplicate
                        </Typography>
                    </a>
                </Grid>
                <ShowOnly when={showDisputeClaim}>
                    <Grid item className={classes.actionItemWrapper}>
                        <a
                            href={makeDisputeClaimEmailLink(osId)}
                            className={classes.actionItem}
                            data-testid="contribute-dispute-claim"
                        >
                            <ShieldXIcon className={classes.actionIcon} />
                            <Typography
                                variant="body1"
                                className={classes.actionLabel}
                            >
                                Dispute Claim
                            </Typography>
                        </a>
                    </Grid>
                </ShowOnly>
                <Grid item className={classes.actionItemWrapper}>
                    <div
                        role="button"
                        tabIndex={0}
                        onClick={openDialog}
                        onKeyDown={e => e.key === 'Enter' && openDialog()}
                        className={classes.actionItem}
                        data-testid="contribute-report-status"
                    >
                        {isClosed ? (
                            <CheckCircleOutline
                                className={classes.actionIcon}
                            />
                        ) : (
                            <HighlightOff className={classes.actionIcon} />
                        )}
                        <Typography
                            variant="body1"
                            className={classes.actionLabel}
                        >
                            {isClosed ? 'Report Reopened' : 'Report Closed'}
                        </Typography>
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
