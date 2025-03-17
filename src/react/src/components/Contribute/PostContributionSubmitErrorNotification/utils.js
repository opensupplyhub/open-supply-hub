import partition from 'lodash/partition';
import isEmpty from 'lodash/isEmpty';
import uniq from 'lodash/uniq';

import { API_V1_ERROR_REQUEST_SOURCE_ENUM } from '../../../util/constants';
import { snakeToTitleCase } from '../../../util/util';

const formPostContributionErrorNotificationContent = errorObj => {
    const errorNotificationContent = {
        errorType: null,
        invalidFields: null,
        nonFieldErrorDetails: null,
        highLevelDetail: null,
        rawData: null,
    };

    console.log('Log errorObj in formPostContributionErrorNotificationContent');
    console.log(errorObj);
    if (errorObj.errorSource === API_V1_ERROR_REQUEST_SOURCE_ENUM.CLIENT) {
        console.log('I am preparing the error content: Client error.');
        errorNotificationContent.errorType = errorObj.errorSource;
        errorNotificationContent.rawData = errorObj.rawData;
        if (!isEmpty(errorObj.errors)) {
            const partitionCondition = error =>
                error.field !== 'non_field_errors';
            const [fieldSpecificErrors, nonFieldErrors] = partition(
                errorObj.errors,
                partitionCondition,
            );

            if (!isEmpty(fieldSpecificErrors)) {
                errorNotificationContent.invalidFields = uniq(
                    fieldSpecificErrors.map(error =>
                        snakeToTitleCase(error.field),
                    ),
                );
            }
            if (!isEmpty(nonFieldErrors)) {
                errorNotificationContent.nonFieldErrorDetails = uniq(
                    nonFieldErrors.map(error => error.detail),
                );
            }
        } else {
            errorNotificationContent.highLevelDetail = errorObj.detail;
        }
        return errorNotificationContent;
    }

    if (errorObj.errorSource === API_V1_ERROR_REQUEST_SOURCE_ENUM.SERVER) {
        console.log('I am preparing the error content: Server error.');
        errorNotificationContent.errorType = errorObj.errorSource;
        errorNotificationContent.rawData = errorObj.rawData;
        return errorNotificationContent;
    }

    console.log('I am preparing the error content: Unknown error.');
    return errorNotificationContent;
};

export default formPostContributionErrorNotificationContent;
