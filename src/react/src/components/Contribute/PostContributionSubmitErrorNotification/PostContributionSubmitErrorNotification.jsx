import React from 'react';
import isEmpty from 'lodash/isEmpty';
import { withStyles } from '@material-ui/core/styles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import Circle from '@material-ui/icons/Circle';
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
    const errorNotificationContent = formPostContributionErrorNotificationContent(
        errorObj,
    );

    if (
        errorNotificationContent.errorType ===
        API_V1_ERROR_REQUEST_SOURCE_ENUM.CLIENT
    ) {
        if (
            !isEmpty(errorNotificationContent.invalidFields) ||
            !isEmpty(errorNotificationContent.nonFieldErrorDetails)
        ) {
            return (
                <NotificationContainer showNotification={showNotification}>
                    <ErrorContent
                        title={ERROR_CONTENT_COPIES.validation.title}
                        supportInstructions={
                            ERROR_CONTENT_COPIES.validation.supportInstructions
                        }
                        rawErrorData={errorNotificationContent.rawData}
                    >
                        {!isEmpty(errorNotificationContent.invalidFields) && (
                            <>
                                <Typography className={classes.mainText}>
                                    {
                                        ERROR_CONTENT_COPIES.validation
                                            .fieldErrorSubtitle
                                    }
                                </Typography>
                                <List
                                    className={`${classes.mainText} ${classes.errorList}`}
                                >
                                    {errorNotificationContent.invalidFields.map(
                                        field => (
                                            <ListItem key={field}>
                                                <ListItemIcon>
                                                    <Circle />
                                                </ListItemIcon>
                                                {field}
                                            </ListItem>
                                        ),
                                    )}
                                </List>
                            </>
                        )}
                        {!isEmpty(
                            errorNotificationContent.nonFieldErrorDetails,
                        ) && (
                            <>
                                <Typography className={classes.mainText}>
                                    {
                                        ERROR_CONTENT_COPIES.validation
                                            .nonFieldErrorSubtitle
                                    }
                                </Typography>
                                <List
                                    className={`${classes.mainText} ${classes.errorList}`}
                                >
                                    {errorNotificationContent.nonFieldErrorDetails.map(
                                        detail => (
                                            <ListItem key={detail}>
                                                <ListItemIcon>
                                                    <Circle />
                                                </ListItemIcon>
                                                {detail}
                                            </ListItem>
                                        ),
                                    )}
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
                    rawErrorData={errorNotificationContent.rawData}
                >
                    <Typography className={classes.mainText}>
                        {ERROR_CONTENT_COPIES.highLevel.subtitle}
                    </Typography>
                    <Typography className={classes.mainText}>
                        {errorNotificationContent.highLevelDetail}
                    </Typography>
                </ErrorContent>
            </NotificationContainer>
        );
    }

    if (
        errorNotificationContent.errorType ===
        API_V1_ERROR_REQUEST_SOURCE_ENUM.SERVER
    ) {
        return (
            <NotificationContainer showNotification={showNotification}>
                <ErrorContent
                    title={ERROR_CONTENT_COPIES.server.title}
                    supportInstructions={
                        ERROR_CONTENT_COPIES.server.supportInstructions
                    }
                    rawErrorData={errorNotificationContent.rawData}
                >
                    <Typography className={classes.mainText}>
                        {ERROR_CONTENT_COPIES.server.body}
                    </Typography>
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
                <Typography className={classes.mainText}>
                    {ERROR_CONTENT_COPIES.uknown.body}
                </Typography>
            </ErrorContent>
        </NotificationContainer>
    );
};

export default withStyles(postContributionSubmitErrorNotificationStyles)(
    PostContributionSubmitErrorNotification,
);
