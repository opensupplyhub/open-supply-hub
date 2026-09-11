import React from 'react';
import { number } from 'prop-types';
import Typography from '@material-ui/core/Typography';
import Paper from '@material-ui/core/Paper';

import { facilityClaimAttachmentsPropType } from '../util/propTypes';
import { makeFacilityClaimAttachmentDownloadURL } from '../util/util';

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

export default function DashboardClaimsDetailsAttachments({
    claimId,
    attachments,
}) {
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
                        <li key={attachment.id}>
                            <Typography variant="body1">
                                {/*
                                    The API responds with a short-lived
                                    redirect to the file after checking the
                                    viewer is authorized; attachments carry
                                    no direct storage URLs (OSDEV-3370).
                                */}
                                <a
                                    href={makeFacilityClaimAttachmentDownloadURL(
                                        claimId,
                                        attachment.id,
                                    )}
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
    claimId: number.isRequired,
    attachments: facilityClaimAttachmentsPropType,
};
