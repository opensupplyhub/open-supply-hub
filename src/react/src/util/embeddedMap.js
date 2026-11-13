import sortBy from 'lodash/sortBy';
import isNil from 'lodash/isNil';
import get from 'lodash/get';

import { OARFont, DEFAULT_SEARCH_TEXT } from './constants';

export const DEFAULT_WIDTH = '1000';

// Must be kept in sync with EmbedField.DISPLAY_AS_CHOICES in
// django/api/models/embed_field.py
export const DISPLAY_AS_TEXT = 'text';
export const DISPLAY_AS_BLURB = 'blurb';
export const DISPLAY_AS_OPTIONS = [
    { value: DISPLAY_AS_TEXT, label: 'Text' },
    { value: 'tags', label: 'Tags' },
    { value: DISPLAY_AS_BLURB, label: 'Blurb' },
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
            colorByField: '',
            colorByColors: {},
            markerColor: '',
            defaultSort: '',
            blurbsFirst: false,
            allowVisitorSort: false,
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
        // '' means every marker shares one color.
        colorByField: embedConfig.color_by_field || '',
        colorByColors: embedConfig.color_by_colors || {},
        // '' means the markers use the primary color.
        markerColor: embedConfig.marker_color || '',
        // '' means the list is sorted by name.
        defaultSort: embedConfig.default_sort || '',
        blurbsFirst: !!embedConfig.blurbs_first,
        allowVisitorSort: !!embedConfig.allow_visitor_sort,
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
        filterable: !!field.filterable,
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

// `fieldsWithData` is the subset of fields the contributor has data for. When
// it is given, each field is flagged with `hasData` and the fields with data
// are listed first, keeping the contributor's order within each group. A field
// without data shows nothing on the map, so its place in the order is moot.
export const combineEmbedAndNonstandardFields = (
    embedFields,
    nonstandardFields,
    fieldsWithData,
) => {
    const existingFields = formatExistingFields(embedFields);
    const newFields = filterAndFormatNonstandardFields({
        nonstandardFields,
        existingFields,
    });
    const combined = sortBy([...existingFields, ...newFields], f => f.order);
    if (!fieldsWithData) {
        return combined.map((f, i) => ({
            ...f,
            order: f.order || i,
        }));
    }
    const withData = new Set(fieldsWithData);
    const flagged = combined.map(f => ({
        ...f,
        hasData: withData.has(f.columnName),
    }));
    return [
        ...flagged.filter(f => f.hasData),
        ...flagged.filter(f => !f.hasData),
    ].map((f, i) => ({ ...f, order: i }));
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
        filterable: !!f.filterable,
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
    default_sort: embedConfig.defaultSort || null,
    blurbs_first: !!embedConfig.blurbsFirst,
    allow_visitor_sort: !!embedConfig.allowVisitorSort,
    marker_color: embedConfig.markerColor || null,
    color_by_field: embedConfig.colorByField || null,
    color_by_colors: embedConfig.colorByField
        ? embedConfig.colorByColors || {}
        : {},
});

export const getErrorMessage = e => e.response.data || e.message;

// A blurb is brand-written text shown publicly, so it is capped.
export const MAX_BLURB_LENGTH = 600;

export const truncateBlurb = text => {
    const blurb = String(text).trim();
    return blurb.length > MAX_BLURB_LENGTH
        ? `${blurb.slice(0, MAX_BLURB_LENGTH).trimEnd()}…`
        : blurb;
};

// A tags field holds several values in one cell, separated by | ; or ,
export const splitTagValues = value =>
    String(value)
        .split(/[|;,]/)
        .map(tag => tag.trim())
        .filter(Boolean);

const hasValue = value => !isNil(value) && String(value).trim() !== '';

// The fields to show on a facility in the search results list: visible
// fields marked "In list" that have a value for this facility, in the
// contributor's order.
export const getListFields = (embedFields, contributorFields) =>
    sortBy(
        (embedFields || []).filter(f => f.visible && f.show_in_list),
        f => f.order,
    )
        .map(f => {
            const match = (contributorFields || []).find(
                cf => cf.fieldName === f.column_name,
            );
            return {
                columnName: f.column_name,
                label: f.display_name,
                value: match ? match.value : null,
                displayAs: f.display_as || DISPLAY_AS_TEXT,
            };
        })
        .filter(f => hasValue(f.value));

// ---------------------------------------------------------------------------
// Supply chains
// ---------------------------------------------------------------------------
// A published chain, as the embed config returns it:
// { id, name, description, product_url, color,
//   nodes: [{ os_id, name, address, country_name, lat, lng, stage, tier }],
//   links: [[supplier os_id, customer os_id]] }

export const getEmbedSupplyChains = (embed, config) =>
    embed && config && Array.isArray(config.supply_chains)
        ? config.supply_chains.filter(chain => chain.nodes.length > 0)
        : [];

export const findEmbedSupplyChain = (chains, id) =>
    (chains || []).find(chain => String(chain.id) === String(id)) || null;

// How many links a location is from the end of the chain: 1 for a location
// that supplies nothing further, 2 for one that supplies it, and so on. Used
// to group a chain's locations when the contributor has no tier field.
export const getChainDepths = chain => {
    const customers = {};
    chain.links.forEach(([supplier, customer]) => {
        customers[supplier] = [...(customers[supplier] || []), customer];
    });
    const depths = {};
    const depthOf = (osId, seen) => {
        if (depths[osId]) return depths[osId];
        if (seen.has(osId)) return 1;
        seen.add(osId);
        const next = customers[osId] || [];
        depths[osId] = next.length
            ? 1 + Math.max(...next.map(id => depthOf(id, seen)))
            : 1;
        return depths[osId];
    };
    chain.nodes.forEach(node => depthOf(node.os_id, new Set()));
    return depths;
};

// A chain's locations in groups, upstream first, for the list. Each group is
// { label, nodes }, and each node gains `supplies`, the names of the locations
// it feeds. Grouped by the contributor's tier value when every location has
// one, otherwise by position in the chain.
export const getChainGroups = chain => {
    const names = {};
    chain.nodes.forEach(node => {
        names[node.os_id] = node.name;
    });
    const withSupplies = chain.nodes.map(node => ({
        ...node,
        supplies: chain.links
            .filter(([supplier]) => supplier === node.os_id)
            .map(([, customer]) => names[customer]),
    }));

    const hasTiers = withSupplies.every(node => hasValue(node.tier));
    const depths = getChainDepths(chain);
    const keyOf = node => (hasTiers ? String(node.tier) : depths[node.os_id]);
    const keys = [...new Set(withSupplies.map(keyOf))].sort((a, b) =>
        hasTiers
            ? String(b).localeCompare(String(a), undefined, { numeric: true })
            : b - a,
    );

    return keys.map(key => ({
        label: hasTiers ? `Tier ${key}` : `Step ${keys.indexOf(key) + 1}`,
        nodes: withSupplies.filter(node => keyOf(node) === key),
    }));
};

// Only http(s) links are ever shown to visitors.
export const getSafeProductUrl = url =>
    /^https?:\/\/[^\s"<>]+$/i.test((url || '').trim()) ? url.trim() : '';

// The dropdown filters an embedded map offers: the contributor's visible,
// filterable fields that have at least one value, in the contributor's order.
// `filterOptions` is `filter_options` from the embed config:
// { column: [{ value, count }] }.
export const getEmbedFieldFilters = (embedFields, filterOptions) =>
    sortBy(
        (embedFields || []).filter(f => f.visible && f.filterable),
        f => f.order,
    )
        .map(f => ({
            columnName: f.column_name,
            label: f.display_name,
            options: ((filterOptions || {})[f.column_name] || []).map(
                ({ value, count }) => ({
                    value,
                    label: `${value} (${count})`,
                }),
            ),
        }))
        .filter(f => f.options.length > 0);

// An embedded map asks for its list in the contributor's chosen order with
// this sort value; the server resolves it.
export const EMBED_DEFAULT_SORT = 'embed_default';

export const EMBED_DEFAULT_SORT_OPTION = Object.freeze({
    value: EMBED_DEFAULT_SORT,
    label: 'Default order',
});

// What a visitor can pick when the contributor lets them change the order.
export const EMBED_VISITOR_SORT_OPTIONS = Object.freeze([
    EMBED_DEFAULT_SORT_OPTION,
    { value: 'name_asc', label: 'A to Z' },
    { value: 'name_desc', label: 'Z to A' },
]);

// A field shown as a blurb the contributor has data for and includes.
const isShownBlurb = f =>
    f.visible && f.hasData !== false && f.displayAs === DISPLAY_AS_BLURB;

// Whether "blurbed facilities first" has anything to act on.
export const hasBlurbField = fields => (fields || []).some(isShownBlurb);

// The orders a contributor can choose for their list: by name, or by any
// field they show, in either direction. A blurb is not offered: a facility
// either has one or not, which "blurbed facilities first" covers. `fields`
// are the settings-screen fields ({ columnName, displayName, visible,
// hasData, displayAs }).
export const getDefaultSortOptions = fields => [
    { value: '', label: 'Name, A to Z' },
    { value: 'name_desc', label: 'Name, Z to A' },
    ...(fields || [])
        .filter(f => f.visible && f.hasData !== false && !isShownBlurb(f))
        .flatMap(f => [
            {
                value: `field:${f.columnName}`,
                label: `${f.displayName}, lowest first`,
            },
            {
                value: `-field:${f.columnName}`,
                label: `${f.displayName}, highest first`,
            },
        ]),
];

// Marker colors used for a field's values until the contributor picks their
// own, in the order the values are listed.
export const COLOR_BY_PALETTE = [
    '#14507a',
    '#2a9d8f',
    '#d98b1f',
    '#8e44ad',
    '#c0392b',
    '#5b6abf',
    '#3f7d20',
    '#b0477f',
];

// The marker color for each value of the field an embedded map is colored
// by: [{ value, color, count }]. `options` is `color_by_options` from the
// embed config and `colors` is the contributor's own choices, { value: hex }.
export const getColorByLegend = (options, colors) =>
    (options || []).map(({ value, count }, i) => ({
        value,
        count,
        color:
            (colors || {})[value] ||
            COLOR_BY_PALETTE[i % COLOR_BY_PALETTE.length],
    }));

// The legend for an embedded map, from its config as the API returns it.
export const getEmbedColorLegend = config =>
    config && config.color_by_field
        ? getColorByLegend(config.color_by_options, config.color_by_colors)
        : [];

export const getEmbedColorLabel = config => {
    if (!config || !config.color_by_field) return '';
    const field = (config.embed_fields || []).find(
        f => f.column_name === config.color_by_field,
    );
    return field ? field.display_name : config.color_by_field;
};

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

// The switches two changes to every embedded map sit behind, whatever its
// package: drawing facilities as dots, and opening a location on the
// production location page layout. Both are off until turned on.
export const EMBED_FACILITY_DOTS_SWITCH = 'embed_facility_dots';

// Whether an embedded map draws its facilities as dots at every zoom level,
// in place of the grouped grid and pins.
export const embedDrawsDots = (embed, featureFlags) =>
    !!embed &&
    !!get(featureFlags, `flags.${EMBED_FACILITY_DOTS_SWITCH}`, false);

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

// App.css squares every <button> with `border-radius: 0 !important`, so a
// button needs !important on its own class to take the embed's corner style.
export const embedButtonCornerStyle = theme => {
    const { cornerRadius } = themeEmbedStyle(theme);
    return isNil(cornerRadius)
        ? {}
        : { borderRadius: `${cornerRadius}px !important` };
};
