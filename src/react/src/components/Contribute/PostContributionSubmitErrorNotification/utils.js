import partition from 'lodash/partition';
import isEmpty from 'lodash/isEmpty';
import uniq from 'lodash/uniq';

import { API_V1_ERROR_REQUEST_SOURCE_ENUM } from '../../../util/constants';
import { snakeToTitleCase } from '../../../util/util';

const formPostContributionErrorNotificationContent = errorObj => {
    const { errorSource, rawData, errors, detail } = errorObj;

    const errorNotificationContent = {
        errorType: errorSource,
        rawData,
        invalidFields: null,
        nonFieldErrorDetails: null,
        highLevelDetail: null,
    };

    if (errorSource === API_V1_ERROR_REQUEST_SOURCE_ENUM.CLIENT) {
        if (!isEmpty(errors)) {
            const [fieldSpecificErrors, nonFieldErrors] = partition(
                errors,
                error => error.field !== 'non_field_errors',
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
            errorNotificationContent.highLevelDetail = detail;
        }
    }

    return errorNotificationContent;
};

export default formPostContributionErrorNotificationContent;
