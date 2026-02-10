import UriProperty from '../FormatComponents/UriProperty';
import UriReferenceProperty from '../FormatComponents/UriReferenceProperty/UriReferenceProperty';
import DateProperty from '../FormatComponents/DateProperty';
import DateTimeProperty from '../FormatComponents/DateTimeProperty/DateTimeProperty';
import IntegerProperty from '../TypeComponents/IntegerProperty/IntegerProperty';
import NestedObjectProperty from '../TypeComponents/NestedObjectProperty/NestedObjectProperty';
import DefaultProperty from '../TypeComponents/DefaultProperty/DefaultProperty';

export const FORMAT_TYPES = {
    URI: 'uri',
    URI_REFERENCE: 'uri-reference',
    DATE: 'date',
    DATE_TIME: 'date-time',
};

export const FORMAT_COMPONENTS = {
    [FORMAT_TYPES.URI]: UriProperty,
    [FORMAT_TYPES.URI_REFERENCE]: UriReferenceProperty,
    [FORMAT_TYPES.DATE]: DateProperty,
    [FORMAT_TYPES.DATE_TIME]: DateTimeProperty,
};

export const TYPE_COMPONENTS = {
    integer: IntegerProperty,
    object: NestedObjectProperty,
};

export const DEFAULT_COMPONENT = DefaultProperty;
