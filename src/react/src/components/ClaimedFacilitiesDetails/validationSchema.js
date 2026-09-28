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
// value made only of them is caught before the request is sent. Both
// fields are required while they are shown: the form pre-fills them with
// the values currently listed for the location, so the claimant always
// submits a name and an address.
const PUNCTUATION_ONLY = /^[\s\-/',:"]*$/;

const claimedTextSchema = label =>
    Yup.string()
        .nullable()
        .test('required', `${label} is required`, value =>
            Boolean((value || '').trim()),
        )
        .max(
            CLAIMED_TEXT_MAX_LENGTH,
            `${label} must be ${CLAIMED_TEXT_MAX_LENGTH} characters or fewer`,
        )
        .test(
            'not-punctuation-only',
            `${label} cannot consist solely of punctuation or whitespace`,
            value => !(value || '').trim() || !PUNCTUATION_ONLY.test(value),
        );

// The fields the form always shows. The component validates with this
// schema while the English name and address are hidden (switch off), so a
// stored value the form cannot display never blocks Save silently.
export const claimedFacilityDetailsBaseSchema = Yup.object().shape({
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

const claimedFacilityDetailsSchema = claimedFacilityDetailsBaseSchema.concat(
    Yup.object().shape({
        facility_name_english: claimedTextSchema('Facility name'),
        facility_address: claimedTextSchema('Facility address'),
    }),
);

export default claimedFacilityDetailsSchema;
