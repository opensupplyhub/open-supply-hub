import { EMPTY_PLACEHOLDER, DATE_FORMATS } from '../util/constants';
import { formatDate } from '../util/util';

const xlsxHeaders = Object.freeze([
    'Claim ID',
    'Facility Name',
    'Organization Name',
    'Country',
    'Created',
    'Claim Decision',
    'Status',
    'Last Updated',
]);

const formatFacilityClaimsDataForXLSX = facilityClaims =>
    [xlsxHeaders].concat(
        facilityClaims.map(facilityClaim => [
            facilityClaim.id,
            facilityClaim.facility_name,
            facilityClaim.contributor_name,
            facilityClaim.facility_country_name,
            formatDate(facilityClaim.created_at, DATE_FORMATS.LONG),
            facilityClaim.claim_decision !== null
                ? formatDate(facilityClaim.claim_decision, DATE_FORMATS.LONG)
                : EMPTY_PLACEHOLDER,
            facilityClaim.status,
            formatDate(facilityClaim.updated_at, DATE_FORMATS.LONG),
        ]),
    );

export default formatFacilityClaimsDataForXLSX;
