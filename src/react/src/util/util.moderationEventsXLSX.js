import { EMPTY_PLACEHOLDER } from './constants';
import { formatDate } from './util';

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

const formatModerationEventsDataForXLSX = moderationEvents =>
    [xlsxHeaders].concat(
        moderationEvents.map(moderationEvent => [
            formatDate(moderationEvent.created_at, 'LL'),
            moderationEvent.name,
            moderationEvent.country.name,
            moderationEvent.contributor_name,
            moderationEvent.match_status,
            moderationEvent.moderation_status,
            moderationEvent.moderation_decision_date !== null
                ? formatDate(moderationEvent.moderation_decision_date, 'LL')
                : EMPTY_PLACEHOLDER,
            formatDate(moderationEvent.updated_at, 'LL'),
        ]),
    );

export default formatModerationEventsDataForXLSX;
