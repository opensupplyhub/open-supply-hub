import moment from 'moment';

const xlsxHeaders = Object.freeze([
    'Claim ID',
    'Facility Name',
    'Organization Name',
    'Country',
    'Created',
    'Last Updated',
    'Status',
]);

const formatFacilityClaimsDataForXLSX = facilityClaims =>
    [xlsxHeaders].concat(
        facilityClaims.map(facilityClaim => [
            facilityClaim.id,
            facilityClaim.facility_name,
            facilityClaim.contributor_name,
            facilityClaim.facility_country_name,
            moment(facilityClaim.created_at).format('LL'),
            moment(facilityClaim.updated_at).format('LL'),
            facilityClaim.status,
        ]),
    );

export default formatFacilityClaimsDataForXLSX;
