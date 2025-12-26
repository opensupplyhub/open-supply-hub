import * as Yup from 'yup';
import isEmpty from 'lodash/isEmpty';
import { isEmail } from 'validator';

import {
    isValidFacilityURL,
    isValidNumberOfWorkers,
    getNumberOfWorkersValidationError,
} from '../../util/util';

const claimedFacilityDetailsSchema = Yup.object().shape({
    facility_website: Yup.string()
        .nullable()
        .test('is-valid-url', 'Invalid website URL', value =>
            isEmpty(value) ? true : isValidFacilityURL(value),
        ),
    point_of_contact_email: Yup.string()
        .nullable()
        .test('is-valid-email', 'Invalid email address', value =>
            isEmpty(value) ? true : isEmail(value),
        ),
    facility_workers_count: Yup.string()
        .nullable()
        .test('is-valid-workers', function facilityWorkersCount(value) {
            if (isEmpty(value)) return true;
            if (isValidNumberOfWorkers(value)) return true;
            return this.createError({
                message: getNumberOfWorkersValidationError(value),
            });
        }),
});

export default claimedFacilityDetailsSchema;
