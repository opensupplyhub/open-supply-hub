/* eslint no-unused-vars: 0 */
import React, { useEffect } from 'react';
import { connect } from 'react-redux';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';

const dashboardClaimsDetailsAttachmentsStyles = Object.freeze({
    containerStyles: Object.freeze({
        width: '100%',
        padding: '25px',
        marginTop: '20px',
    }),
});

function DashboardClaimsDetailsAttachments() {
    return (
        <Paper style={dashboardClaimsDetailsAttachmentsStyles.containerStyles}>
            <Typography variant="title">Claim documentation</Typography>
            <Typography variant="body1">
                Link to the attachments to upload
            </Typography>
        </Paper>
    );
}

/*
DashboardClaimsDetailsAttachments.defaultProps = {};

DashboardClaimsDetailsAttachments.propTypes = {};
*/

export default connect(null, null)(DashboardClaimsDetailsAttachments);
