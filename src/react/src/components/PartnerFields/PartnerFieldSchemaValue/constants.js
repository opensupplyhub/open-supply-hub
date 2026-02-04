import UriProperty from '../FormatComponents/UriProperty/UriProperty';
import UriReferenceProperty from '../FormatComponents/UriReferenceProperty/UriReferenceProperty';
import DateProperty from '../FormatComponents/DateProperty/DateProperty';
import DateTimeProperty from '../FormatComponents/DateTimeProperty/DateTimeProperty';
import IntegerProperty from '../TypeComponents/IntegerProperty/IntegerProperty';
import NestedObjectProperty from '../TypeComponents/NestedObjectProperty/NestedObjectProperty';
import DefaultProperty from '../TypeComponents/DefaultProperty/DefaultProperty';

/**
 * Format constants for JSON Schema.
 */
export const FORMAT_TYPES = {
    URI: 'uri',
    URI_REFERENCE: 'uri-reference',
    DATE: 'date',
    DATE_TIME: 'date-time',
};

/**
 * Format component registry.
 * Maps format types to their component functions.
 */
export const FORMAT_COMPONENTS = {
    [FORMAT_TYPES.URI]: UriProperty,
    [FORMAT_TYPES.URI_REFERENCE]: UriReferenceProperty,
    [FORMAT_TYPES.DATE]: DateProperty,
    [FORMAT_TYPES.DATE_TIME]: DateTimeProperty,
};

/**
 * Type component registry.
 * Maps schema types to their component functions.
 */
export const TYPE_COMPONENTS = {
    integer: IntegerProperty,
    object: NestedObjectProperty,
};

/**
 * Default component for unknown types
 */
export const DEFAULT_COMPONENT = DefaultProperty;
