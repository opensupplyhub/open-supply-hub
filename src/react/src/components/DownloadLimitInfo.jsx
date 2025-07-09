import React from 'react';
import { object } from 'prop-types';
import { withStyles, Grid } from '@material-ui/core';

import { FREE_FACILITIES_DOWNLOAD_LIMIT } from '../util/constants';
import { downloadLimitInfoStyles } from '../util/styles';

const DownloadLimitInfo = ({ classes }) => (
    <Grid container className={classes.informativeWrapper}>
        <Grid item className={classes.informativeText}>
            <p>
                All registered accounts can download up to{' '}
                {FREE_FACILITIES_DOWNLOAD_LIMIT} production locations annually
                for free.
            </p>
            <p className={classes.informativeTextBold}>
                This search includes more production locations than you have
                available for download. You may purchase additional downloads to
                continue.
            </p>
            <p className={classes.informativeTextSmall}>
                If you are from a civil society organization or research
                institution, you may qualify for discounted or unlimited free
                download access.{' '}
                <a
                    href="https://info.opensupplyhub.org/governance-policies"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    Learn more and apply
                </a>
                .
            </p>
        </Grid>
    </Grid>
);

DownloadLimitInfo.propTypes = {
    classes: object.isRequired,
};

export default withStyles(downloadLimitInfoStyles)(DownloadLimitInfo);
