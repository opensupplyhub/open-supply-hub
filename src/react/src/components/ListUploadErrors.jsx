import React from 'react';

import { withStyles } from '@material-ui/core/styles';

import { listUploadTroubleshootingEmail } from '../util/constants';

const listUploadErrorsStyles = () => ({
    errorItem: {
        color: 'red',
    },
    postErrorHelp: {
        margin: '1.5rem 0',
        fontWeight: 500,
    },
});

const ListUploadErrors = ({ errors, classes }) => (
    <>
        <ul>
            {errors.map(err => (
                <li key={err} className={classes.errorItem}>
                    {err}
                </li>
            ))}
        </ul>
        <div className={classes.postErrorHelp}>
            If you continue to have trouble submitting your list, please email{' '}
            <a href={`mailto:${listUploadTroubleshootingEmail}`}>
                {listUploadTroubleshootingEmail}
            </a>
            .
        </div>
    </>
);

export default withStyles(listUploadErrorsStyles)(ListUploadErrors);
