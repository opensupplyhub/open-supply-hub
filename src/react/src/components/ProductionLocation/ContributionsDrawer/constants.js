export const DEFAULT_TITLE = 'All Data Sources';
export const PROMOTED_SECTION_LABEL = 'Highlighted Data Source';
export const CONTRIBUTIONS_SECTION_LABEL = 'Other Data Sources';
export const INFO_PROMOTED_TITLE = 'Why is this data source displayed first?';
export const INFO_CONTRIBUTIONS_TEXT =
    'Multiple organizations may have shared information for this data point. You can see the list of historical data sources below. Click on the organization name to learn more about them and the data they have shared';
export const LEARN_MORE_LABEL = 'Learn more about our open data model';
export const LEARN_MORE_OPEN_DATA_MODEL_URL =
    'https://info.opensupplyhub.org/resources/an-open-data-model';

/**
 * Per-row provenance of the FacilityListItem a contribution came from
 * (OSDEV-3073). Rendered in display order; only fields present on the
 * contribution are shown.
 */
export const PROVENANCE_FIELD_LABELS = Object.freeze([
    Object.freeze({ key: 'source_name', label: 'Source' }),
    Object.freeze({ key: 'source_link', label: 'Source link', isLink: true }),
    Object.freeze({ key: 'information_source_type', label: 'Source type' }),
    Object.freeze({ key: 'date_of_source', label: 'Date of source' }),
    Object.freeze({ key: 'notes', label: 'Notes' }),
    Object.freeze({
        key: 'data_collection_methodology',
        label: 'Data collection methodology',
    }),
    Object.freeze({ key: 'ai_usage_notes', label: 'AI usage notes' }),
]);
