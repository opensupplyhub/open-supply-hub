import React from 'react';
import isEmpty from 'lodash/isEmpty';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import LensIcon from '@material-ui/icons/Lens';
import Typography from '@material-ui/core/Typography';
import NotificationContainer from './NotificationContainer';
import ErrorContent from './ErrorContent';
import formPostContributionErrorNotificationContent from './utils';
import { API_V1_ERROR_REQUEST_SOURCE_ENUM } from '../../../util/constants';
import ERROR_CONTENT_COPIES from './constants';
import { postContributionSubmitErrorNotificationStyles } from './styles';

const PostContributionSubmitErrorNotification = ({
    showNotification,
    errorObj,
    classes,
}) => {
    const {
        errorType,
        rawData,
        invalidFields,
        nonFieldErrorDetails,
        highLevelDetail,
    } = formPostContributionErrorNotificationContent(errorObj);

    if (errorType === API_V1_ERROR_REQUEST_SOURCE_ENUM.CLIENT) {
        if (!isEmpty(invalidFields) || !isEmpty(nonFieldErrorDetails)) {
            return (
                <NotificationContainer showNotification={showNotification}>
                    <ErrorContent
                        title={ERROR_CONTENT_COPIES.validation.title}
                        supportInstructions={
                            ERROR_CONTENT_COPIES.validation.supportInstructions
                        }
                        rawErrorData={rawData}
                    >
                        {!isEmpty(invalidFields) && (
                            <>
                                <Typography>
                                    {
                                        ERROR_CONTENT_COPIES.validation
                                            .fieldErrorSubtitle
                                    }
                                </Typography>
                                <List className={classes.errorList}>
                                    {invalidFields.map(field => (
                                        <ListItem key={field}>
                                            <ListItemIcon>
                                                <LensIcon
                                                    className={
                                                        classes.bulletIcon
                                                    }
                                                />
                                            </ListItemIcon>
                                            <Typography>{field}</Typography>
                                        </ListItem>
                                    ))}
                                </List>
                            </>
                        )}
                        {!isEmpty(nonFieldErrorDetails) && (
                            <>
                                <Typography>
                                    {
                                        ERROR_CONTENT_COPIES.validation
                                            .nonFieldErrorSubtitle
                                    }
                                </Typography>
                                <List className={classes.errorList}>
                                    {nonFieldErrorDetails.map(detail => (
                                        <ListItem key={detail}>
                                            <ListItemIcon>
                                                <LensIcon
                                                    className={
                                                        classes.bulletIcon
                                                    }
                                                />
                                            </ListItemIcon>
                                            <Typography>{detail}</Typography>
                                        </ListItem>
                                    ))}
                                </List>
                            </>
                        )}
                    </ErrorContent>
                </NotificationContainer>
            );
        }

        // If the "errors" key doesn't exist or doesn't have any value,
        // the root-level "detail" key value will be displayed.
        return (
            <NotificationContainer showNotification={showNotification}>
                <ErrorContent
                    title={ERROR_CONTENT_COPIES.highLevel.title}
                    supportInstructions={
                        ERROR_CONTENT_COPIES.highLevel.supportInstructions
                    }
                    rawErrorData={rawData}
                >
                    <Typography>
                        {ERROR_CONTENT_COPIES.highLevel.subtitle}
                    </Typography>
                    <List className={classes.errorList}>
                        <ListItem>
                            <ListItemIcon>
                                <LensIcon className={classes.bulletIcon} />
                            </ListItemIcon>
                            <Typography>{highLevelDetail}</Typography>
                        </ListItem>
                    </List>
                </ErrorContent>
            </NotificationContainer>
        );
    }

    if (errorType === API_V1_ERROR_REQUEST_SOURCE_ENUM.SERVER) {
        return (
            <NotificationContainer showNotification={showNotification}>
                <ErrorContent
                    title={ERROR_CONTENT_COPIES.server.title}
                    supportInstructions={
                        ERROR_CONTENT_COPIES.server.supportInstructions
                    }
                    rawErrorData={rawData}
                >
                    <Typography>{ERROR_CONTENT_COPIES.server.body}</Typography>
                </ErrorContent>
            </NotificationContainer>
        );
    }

    return (
        <NotificationContainer showNotification={showNotification}>
            <ErrorContent
                title={ERROR_CONTENT_COPIES.uknown.title}
                supportInstructions={
                    ERROR_CONTENT_COPIES.uknown.supportInstructions
                }
            >
                <Typography>{ERROR_CONTENT_COPIES.uknown.body}</Typography>
            </ErrorContent>
        </NotificationContainer>
    );
};

PostContributionSubmitErrorNotification.propTypes = {
    showNotification: func.isRequired,
    errorObj: object.isRequired,
    classes: object.isRequired,
};

export default withStyles(postContributionSubmitErrorNotificationStyles)(
    PostContributionSubmitErrorNotification,
);
