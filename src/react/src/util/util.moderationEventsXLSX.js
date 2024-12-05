import { EMPTY_PLACEHOLDER, DATE_FORMATS } from './constants';
import { formatDate } from './util';

const xlsxHeaders = Object.freeze([
    'Created Date',
    'Location Name',
    'Country',
    'Contributor',
    'Source Type',
    'Moderation Status',
    'Moderation Decision Date',
    'Last Updated',
]);

const formatModerationEventsDataForXLSX = moderationEvents =>
    [xlsxHeaders].concat(
        moderationEvents.map(moderationEvent => [
            formatDate(moderationEvent.created_at, DATE_FORMATS.LONG),
            moderationEvent.cleaned_data.name,
            moderationEvent.cleaned_data.country.name,
            moderationEvent.contributor_name,
            moderationEvent.source,
            moderationEvent.status,
            moderationEvent.status_change_date !== null
                ? formatDate(
                      moderationEvent.status_change_date,
                      DATE_FORMATS.LONG,
                  )
                : EMPTY_PLACEHOLDER,
            formatDate(moderationEvent.updated_at, DATE_FORMATS.LONG),
        ]),
    );

export default formatModerationEventsDataForXLSX;
