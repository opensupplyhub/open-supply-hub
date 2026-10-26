/*
 * Copy for the registered-record entry point.
 *
 * Shared because this text appears on both the legacy facility profile
 * and the production location page. Which of the two a visitor lands on
 * depends on a feature switch, so two copies of the wording would
 * eventually tell two visitors different things about the same record.
 *
 * The styling is deliberately not shared alongside it: the two pages
 * place the panel in different layout contexts and need different
 * container spacing, so each keeps its own rules.
 */

export const IDENTITY_RECORD_ENTRY_TITLE = 'Registered record';

export const IDENTITY_RECORD_ENTRY_TEXT =
    'Another organization has published a record about this location and ' +
    'registered it against this OS ID.';

export const IDENTITY_RECORD_ENTRY_LINK_LABEL = 'View the registered record';
