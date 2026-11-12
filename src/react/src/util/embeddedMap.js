import sortBy from 'lodash/sortBy';
import isNil from 'lodash/isNil';

import { OARFont, DEFAULT_SEARCH_TEXT } from './constants';

export const DEFAULT_WIDTH = '1000';

// Must be kept in sync with EmbedField.DISPLAY_AS_CHOICES in
// django/api/models/embed_field.py
export const DISPLAY_AS_TEXT = 'text';
export const DISPLAY_AS_OPTIONS = [
    { value: DISPLAY_AS_TEXT, label: 'Text' },
    { value: 'tags', label: 'Tags' },
    { value: 'blurb', label: 'Blurb' },
];
export const DEFAULT_HEIGHT = '800';

const getHeight = embedConfig => (embedConfig.height ? embedConfig.height : '');

const formatExistingWidth = ({ width = DEFAULT_WIDTH }) => {
    const fullWidth = width[width.length - 1] === '%';
    if (!width) {
        return { fullWidth, width: '' };
    }
    return { fullWidth, width };
};

export const formatExistingConfig = embedConfig => {
    if (!embedConfig) {
        return {
            width: DEFAULT_WIDTH,
            color: '#3d2f8c',
            font: OARFont,
            height: DEFAULT_HEIGHT,
            hideSectorData: true,
            accentColor: '',
            headingFont: '',
            cornerRadius: '',
        };
    }
    return {
        ...embedConfig,
        ...formatExistingWidth(embedConfig),
        color: embedConfig.color ? embedConfig.color : '#3d2f8c',
        font: embedConfig.font ? embedConfig.font : OARFont,
        height: getHeight(embedConfig),
        preferContributorName: embedConfig.prefer_contributor_name,
        textSearchLabel: embedConfig.text_search_label
            ? embedConfig.text_search_label
            : DEFAULT_SEARCH_TEXT,
        mapStyle: embedConfig.map_style ? embedConfig.map_style : 'default',
        hideSectorData: embedConfig.hide_sector_data,
        // '' means "not set" for all three: the embed keeps its current look.
        accentColor: embedConfig.accent_color || '',
        headingFont: embedConfig.heading_font || '',
        cornerRadius: isNil(embedConfig.corner_radius)
            ? ''
            : embedConfig.corner_radius,
    };
};

export const formatExistingFields = (fields = []) =>
    fields.map(field => ({
        columnName: field.column_name,
        displayName: field.display_name,
        visible: field.visible,
        order: field.order,
        searchable: field.searchable,
        showInList: !!field.show_in_list,
        displayAs: field.display_as || DISPLAY_AS_TEXT,
    }));

const doesExist = (field, existingFields) =>
    existingFields.some(f => f.columnName === field);

// Keys in this object must be kept in sync with the NonstandardField.EXENDED_FIELDS in django/api/models.py
const defaultNonstandardFieldLabels = {
    parent_company: 'Parent Company',
    product_type: 'Product Type',
    number_of_workers: 'Number of Workers',
    facility_type: 'Facility Type',
    processing_type: 'Processing Type',
};

const defaultFormatForNonstandardField = field => ({
    columnName: field,
    displayName: defaultNonstandardFieldLabels[field] || field,
    visible: !!defaultNonstandardFieldLabels[field],
    showInList: false,
    displayAs: DISPLAY_AS_TEXT,
});

const filterAndFormatNonstandardFields = ({
    nonstandardFields,
    existingFields,
}) =>
    nonstandardFields
        .filter(field => !doesExist(field, existingFields))
        .map(defaultFormatForNonstandardField);

export const combineEmbedAndNonstandardFields = (
    embedFields,
    nonstandardFields,
) => {
    const existingFields = formatExistingFields(embedFields);
    const newFields = filterAndFormatNonstandardFields({
        nonstandardFields,
        existingFields,
    });
    return sortBy([...existingFields, ...newFields], f => f.order).map(
        (f, i) => ({
            ...f,
            order: f.order || i,
        }),
    );
};

const formatEmbedFieldsForServer = fields =>
    sortBy(fields, f => f.order).map((f, i) => ({
        visible: f.visible,
        searchable: f.searchable,
        order: i,
        display_name: f.displayName,
        column_name: f.columnName,
        show_in_list: !!f.showInList,
        display_as: f.displayAs || DISPLAY_AS_TEXT,
    }));

// 0 is a real choice (square corners), so only '' and nil mean "not set".
const formatCornerRadiusForServer = cornerRadius =>
    cornerRadius === '' || isNil(cornerRadius) ? null : Number(cornerRadius);

const formatWidthForServer = ({ width, fullWidth }) => {
    if (fullWidth) return '100%';
    if (!width || width === '100%') return '';
    return width;
};

export const formatEmbedConfigForServer = (embedConfig, embedFields) => ({
    ...embedConfig,
    width: formatWidthForServer(embedConfig),
    height: getHeight(embedConfig),
    prefer_contributor_name: embedConfig.preferContributorName,
    embed_fields: formatEmbedFieldsForServer(embedFields),
    text_search_label: embedConfig.textSearchLabel,
    map_style: embedConfig.mapStyle,
    hide_sector_data: embedConfig.hideSectorData,
    accent_color: embedConfig.accentColor || null,
    heading_font: embedConfig.headingFont || null,
    corner_radius: formatCornerRadiusForServer(embedConfig.cornerRadius),
});

export const getErrorMessage = e => e.response.data || e.message;

const NO_EMBED_STYLE = Object.freeze({
    accentColor: null,
    headingFont: null,
    cornerRadius: null,
});

// The style settings the embedded map applies on top of its theme. Outside
// embed mode, and for any setting that is not set, the value is null and each
// component keeps its own style.
export const getEmbedStyle = (embed, config) => {
    if (!embed || !config) return NO_EMBED_STYLE;
    return {
        accentColor: config.accent_color || null,
        headingFont: config.heading_font || null,
        cornerRadius: isNil(config.corner_radius)
            ? null
            : Number(config.corner_radius),
    };
};

// Themes built outside App.jsx (in tests, for example) have no embed style.
export const themeEmbedStyle = theme =>
    (theme && theme.embed) || NO_EMBED_STYLE;

export const embedHeadingFont = theme =>
    themeEmbedStyle(theme).headingFont || theme.typography.fontFamily;

// Spread into a style object: adds a border radius only when one is set.
export const embedCornerStyle = theme => {
    const { cornerRadius } = themeEmbedStyle(theme);
    return isNil(cornerRadius) ? {} : { borderRadius: `${cornerRadius}px` };
};
