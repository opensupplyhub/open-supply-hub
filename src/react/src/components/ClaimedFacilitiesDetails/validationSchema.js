import * as Yup from 'yup';
import isEmpty from 'lodash/isEmpty';
import { isEmail } from 'validator';

import {
    isValidFacilityURL,
    isValidNumberOfWorkers,
    getNumberOfWorkersValidationError,
} from '../../util/util';

export const CLAIMED_TEXT_MAX_LENGTH = 200;

// The backend rejects a claimed name or address that ContriCleaner's clean()
// reduces to nothing; this is the set of characters clean() strips, so a
// value made only of them is caught before the request is sent. Blank and
// whitespace-only values are allowed: the backend stores them as NULL,
// meaning the claimant no longer asserts that value.
const PUNCTUATION_ONLY = /^[\s\-/',:"]*$/;

const claimedTextSchema = label =>
    Yup.string()
        .nullable()
        .max(
            CLAIMED_TEXT_MAX_LENGTH,
            `${label} must be ${CLAIMED_TEXT_MAX_LENGTH} characters or fewer`,
        )
        .test(
            'not-punctuation-only',
            `${label} cannot consist solely of punctuation or whitespace`,
            value => !(value || '').trim() || !PUNCTUATION_ONLY.test(value),
        );

const claimedFacilityDetailsSchema = Yup.object().shape({
    facility_name_english: claimedTextSchema('Facility name'),
    facility_address: claimedTextSchema('Facility address'),
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
