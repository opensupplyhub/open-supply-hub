import React from 'react';
import { v4 as uuidv4 } from 'uuid';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';

import { facilityClaimAttachmentsPropType } from '../util/propTypes';

const dashboardClaimsDetailsAttachmentsStyles = Object.freeze({
    containerStyles: Object.freeze({
        width: '100%',
        padding: '25px',
        marginTop: '20px',
    }),
    attachmentList: Object.freeze({
        listStyle: 'none',
        padding: 0,
    }),
});

export default function DashboardClaimsDetailsAttachments({ attachments }) {
    return (
        <Paper style={dashboardClaimsDetailsAttachmentsStyles.containerStyles}>
            <Typography variant="title">Claim documentation</Typography>
            {attachments.length > 0 ? (
                <ul
                    style={
                        dashboardClaimsDetailsAttachmentsStyles.attachmentList
                    }
                >
                    {attachments.map(attachment => (
                        <li key={uuidv4()}>
                            <Typography variant="body1">
                                <a
                                    href={attachment.claim_attachment}
                                    rel="noreferrer"
                                    target="_blank"
                                >
                                    {attachment.file_name}
                                </a>
                            </Typography>
                        </li>
                    ))}
                </ul>
            ) : (
                <Typography variant="body1">No documents provided</Typography>
            )}
        </Paper>
    );
}

DashboardClaimsDetailsAttachments.defaultProps = {
    attachments: [],
};

DashboardClaimsDetailsAttachments.propTypes = {
    attachments: facilityClaimAttachmentsPropType,
};
