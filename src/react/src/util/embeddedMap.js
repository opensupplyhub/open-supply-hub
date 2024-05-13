import sortBy from 'lodash/sortBy';

import { OARFont, DEFAULT_SEARCH_TEXT } from './constants';

export const DEFAULT_WIDTH = '1000';
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
    };
};

export const formatExistingFields = (fields = []) =>
    fields.map(field => ({
        columnName: field.column_name,
        displayName: field.display_name,
        visible: field.visible,
        order: field.order,
        searchable: field.searchable,
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
    }));

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
});

export const getErrorMessage = e => e.response.data || e.message;
