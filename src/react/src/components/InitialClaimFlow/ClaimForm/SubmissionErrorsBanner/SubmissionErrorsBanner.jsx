import React from 'react';
import { array, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Warning from '@material-ui/icons/Warning';

import { formatSubmissionErrorForDisplay } from '../utils';
import submissionErrorsBannerStyles from './styles';

const SubmissionErrorsBanner = ({ classes, errors }) => {
    const uniqueErrors = errors ? [...new Set(errors)] : [];

    if (uniqueErrors.length === 0) {
        return null;
    }

    return (
        <div className={classes.container}>
            <div className={classes.content}>
                <Typography variant="body2" className={classes.text}>
                    <span className={classes.textIcon}>
                        <Warning className={classes.warningIcon} />
                        <strong>ERROR!</strong>
                    </span>
                    {uniqueErrors.length === 1 ? (
                        <span>
                            {formatSubmissionErrorForDisplay(uniqueErrors[0])}
                        </span>
                    ) : (
                        <span>Please fix the following validation errors:</span>
                    )}
                </Typography>
                {uniqueErrors.length > 1 && (
                    <ul className={classes.errorList}>
                        {uniqueErrors.map(message => (
                            <li key={message}>
                                {formatSubmissionErrorForDisplay(message)}
                            </li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

SubmissionErrorsBanner.defaultProps = {
    errors: null,
};

SubmissionErrorsBanner.propTypes = {
    classes: object.isRequired,
    errors: array,
};

export default withStyles(submissionErrorsBannerStyles)(SubmissionErrorsBanner);
