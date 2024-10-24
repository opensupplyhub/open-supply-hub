import moment from 'moment';

import { EMPTY_PLACEHOLDER } from './constants';

const xlsxHeaders = Object.freeze([
    'Created Date',
    'Location Name',
    'Country',
    'Contributor',
    'Match Status',
    'Moderation Status',
    'Moderation Decision Date',
    'Last Updated',
]);

const formatFacilityClaimsDataForXLSX = moderationEvents =>
    [xlsxHeaders].concat(
        moderationEvents.map(moderationEvent => [
            moment(moderationEvent.created_at).format('LL'),
            moderationEvent.name,
            moderationEvent.country.name,
            moderationEvent.contributor_name,
            moderationEvent.match_status,
            moderationEvent.moderation_status,
            moderationEvent.moderation_decision_date !== null
                ? moment(moderationEvent.moderation_decision_date).format('LL')
                : EMPTY_PLACEHOLDER,
            moment(moderationEvent.updated_at).format('LL'),
        ]),
    );

export default formatFacilityClaimsDataForXLSX;
