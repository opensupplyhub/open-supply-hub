import moment from 'moment';

import { CLAIM_DECISION_EMPTY } from '../util/constants';

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
            moment(facilityClaim.created_at).format('LL'),
            facilityClaim.claim_decision !== null
                ? moment(facilityClaim.claim_decision).format('LL')
                : CLAIM_DECISION_EMPTY,
            facilityClaim.status,
            moment(facilityClaim.updated_at).format('LL'),
        ]),
    );

export default formatFacilityClaimsDataForXLSX;
