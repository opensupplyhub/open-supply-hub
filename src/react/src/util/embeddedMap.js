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
            showSpotlight: false,
            spotlightHighlight: false,
            spotlightFilter: false,
            spotlightGroups: [],
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
        // Spotlight is partner data: off unless the contributor turns it on.
        showSpotlight: !!embedConfig.show_spotlight,
        spotlightHighlight: !!embedConfig.spotlight_highlight,
        spotlightFilter: !!embedConfig.spotlight_filter,
        spotlightGroups: embedConfig.spotlight_groups || [],
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
    show_spotlight: !!embedConfig.showSpotlight,
    spotlight_highlight: !!embedConfig.spotlightHighlight,
    spotlight_filter: !!embedConfig.spotlightFilter,
    spotlight_groups: embedConfig.spotlightGroups || [],
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

    // Tiers are only used when they agree with the links: every supplier in
    // a higher tier than the location it supplies. Otherwise the chain would
    // read out of order.
    const tierOf = {};
    withSupplies.forEach(node => {
        tierOf[node.os_id] = parseFloat(node.tier);
    });
    const hasTiers =
        withSupplies.every(node => hasValue(node.tier)) &&
        chain.links.every(([supplier, customer]) => {
            const from = tierOf[supplier];
            const to = tierOf[customer];
            return Number.isNaN(from) || Number.isNaN(to) || from > to;
        });
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

// ---------------------------------------------------------------------------
// Spotlight: partner data on an embedded map
// ---------------------------------------------------------------------------
// `config.spotlight`, when the contributor shows Spotlight data, is
// { highlight, filter, count, groups: [{ uuid, name, count, field_names }] }.

// The pseudo-column the Spotlight filter is kept under among an embedded
// map's filters. It travels as `embed_spotlight=<value>`, not as a column.
export const EMBED_SPOTLIGHT_FILTER = '__spotlight__';
export const ANY_SPOTLIGHT = 'any';

export const getEmbedSpotlight = (embed, config) =>
    embed && config && config.spotlight ? config.spotlight : null;

// The Spotlight filter's choices, or none when it is not offered or no
// facility has data.
export const getSpotlightFilterOptions = spotlight => {
    if (!spotlight || !spotlight.filter || !spotlight.count) return [];
    return [
        {
            value: ANY_SPOTLIGHT,
            label: `Any partner data (${spotlight.count})`,
        },
        ...spotlight.groups
            .filter(group => group.count > 0)
            .map(group => ({
                value: group.uuid,
                label: `${group.name} (${group.count})`,
            })),
    ];
};

// Whether a facility's details carry any partner data. An embedded map is
// only ever sent the kinds its contributor shows.
export const hasPartnerData = data =>
    Object.values((data && data.properties.partner_fields) || {}).some(
        values => Array.isArray(values) && values.length > 0 && !!values[0],
    );

// Changes when what the map's tiles should flag changes, so they are
// fetched again. Empty when facilities with Spotlight data are not ringed.
export const getSpotlightTileKey = spotlight =>
    spotlight && spotlight.highlight
        ? spotlight.groups.map(group => group.uuid.slice(0, 8)).join('.')
        : '';

// The ring around a facility that has Spotlight data: the map's accent
// color, or its primary color.
export const getSpotlightRingColor = config =>
    (config && (config.accent_color || config.color)) || '#0D1128';

export const toggleSpotlightGroup = (groups, uuid, checked) =>
    checked
        ? [...groups.filter(group => group !== uuid), uuid]
        : groups.filter(group => group !== uuid);

// --- Building a chain in the settings ---

export const DEFAULT_CHAIN_COLOR = '#c0392b';
export const MAX_CHAIN_LOCATIONS = 60;
export const CHAIN_STAGE_SUGGESTIONS = Object.freeze([
    'Raw material',
    'Material production',
    'Processing',
    'Final assembly',
]);

export const makeEmptyChain = () => ({
    name: '',
    description: '',
    product_url: '',
    color: DEFAULT_CHAIN_COLOR,
    is_published: false,
    nodes: [],
    links: [],
});

// Whether following "supplies" links from a location ever leads back to it.
export const chainLinksLoop = links => {
    const customers = {};
    links.forEach(([supplier, customer]) => {
        customers[supplier] = [...(customers[supplier] || []), customer];
    });
    const done = new Set();
    const visit = (osId, path) => {
        if (path.has(osId)) return true;
        if (done.has(osId)) return false;
        const nextPath = new Set(path).add(osId);
        const looped = (customers[osId] || []).some(id => visit(id, nextPath));
        done.add(osId);
        return looped;
    };
    return Object.keys(customers).some(id => visit(id, new Set()));
};

export const addChainLocation = (chain, { osId, name }) =>
    chain.nodes.some(node => node.os_id === osId)
        ? chain
        : {
              ...chain,
              nodes: [...chain.nodes, { os_id: osId, name, stage: '' }],
          };

// Removing a location also removes the links to and from it.
export const removeChainLocation = (chain, osId) => ({
    ...chain,
    nodes: chain.nodes.filter(node => node.os_id !== osId),
    links: chain.links.filter(link => !link.includes(osId)),
});

export const setChainLocationStage = (chain, osId, stage) => ({
    ...chain,
    nodes: chain.nodes.map(node =>
        node.os_id === osId ? { ...node, stage } : node,
    ),
});

export const addChainLink = (chain, supplier, customer) =>
    chain.links.some(([s, c]) => s === supplier && c === customer)
        ? chain
        : { ...chain, links: [...chain.links, [supplier, customer]] };

export const removeChainLink = (chain, supplier, customer) => ({
    ...chain,
    links: chain.links.filter(([s, c]) => !(s === supplier && c === customer)),
});

// The locations `supplier` could be set to supply: any other location it
// does not already supply, where the link would not make the chain loop.
export const getPossibleCustomers = (chain, supplier) =>
    chain.nodes.filter(
        node =>
            node.os_id !== supplier &&
            !chain.links.some(([s, c]) => s === supplier && c === node.os_id) &&
            !chainLinksLoop([...chain.links, [supplier, node.os_id]]),
    );

// Reverse a link, unless that would make the chain loop.
export const reverseChainLink = (chain, supplier, customer) => {
    const others = chain.links.filter(
        ([s, c]) => !(s === supplier && c === customer),
    );
    const reversed = [...others, [customer, supplier]];
    return chainLinksLoop(reversed) ? chain : { ...chain, links: reversed };
};

const tierNumber = tier => {
    const number = parseFloat(tier);
    return Number.isFinite(number) ? number : null;
};

// Which way a new link between the selected location and a clicked one most
// likely runs, as [supplier, customer]. Chains are usually built from the
// final factory backwards, so the clicked location supplies the selected one
// unless their tiers say otherwise (a higher tier supplies a lower one).
export const guessLinkDirection = (selected, clicked) => {
    const selectedTier = tierNumber(selected.tier);
    const clickedTier = tierNumber(clicked.tier);
    return selectedTier !== null &&
        clickedTier !== null &&
        clickedTier < selectedTier
        ? [selected.osId, clicked.osId]
        : [clicked.osId, selected.osId];
};

// What clicking a facility does in the builder. `clicked` and each entry of
// `tiers` come from the contributor's locations: { osId, name, tier }.
// Returns the chain, the location now selected, and a message when the
// click could not do what was asked.
//  - Nothing selected: the facility joins the chain and is selected.
//  - The selected location: it is deselected.
//  - Another facility: it joins the chain if need be, is linked to the
//    selected location, and becomes the selected one, so a chain can be
//    walked from one end to the other. If the two are already linked it is
//    only selected.
export const clickChainLocation = (chain, selectedId, clicked, tiers = {}) => {
    const inChain = chain.nodes.some(node => node.os_id === clicked.osId);
    if (!inChain && chain.nodes.length >= MAX_CHAIN_LOCATIONS) {
        return {
            chain,
            selectedId,
            message: `A supply chain can have at most ${MAX_CHAIN_LOCATIONS} locations.`,
        };
    }
    if (clicked.osId === selectedId) {
        return { chain, selectedId: null, message: '' };
    }
    const withLocation = addChainLocation(chain, clicked);
    const hasSelected = chain.nodes.some(node => node.os_id === selectedId);
    if (!hasSelected) {
        return { chain: withLocation, selectedId: clicked.osId, message: '' };
    }
    const linked = chain.links.some(
        link => link.includes(clicked.osId) && link.includes(selectedId),
    );
    if (linked) {
        return { chain, selectedId: clicked.osId, message: '' };
    }
    const [supplier, customer] = guessLinkDirection(
        { osId: selectedId, tier: tiers[selectedId] },
        { osId: clicked.osId, tier: tiers[clicked.osId] },
    );
    const direction = [
        [supplier, customer],
        [customer, supplier],
    ].find(link => !chainLinksLoop([...withLocation.links, link]));
    if (!direction) {
        return {
            chain,
            selectedId,
            message:
                'Linking those two would make the chain loop back on itself.',
        };
    }
    return {
        chain: addChainLink(withLocation, direction[0], direction[1]),
        selectedId: clicked.osId,
        message: '',
    };
};

// What the builder sends to the API: names are for display only.
export const formatChainForAPI = chain => ({
    name: chain.name.trim(),
    description: chain.description.trim(),
    product_url: chain.product_url.trim(),
    color: chain.color,
    is_published: chain.is_published,
    nodes: chain.nodes.map(node => ({
        os_id: node.os_id,
        stage: node.stage || '',
    })),
    links: chain.links,
});

// Every message in an API error response, whichever field it is about.
export const getChainErrorMessages = data => {
    if (!data || typeof data !== 'object') {
        return ['The supply chain could not be saved.'];
    }
    const messages = Object.values(data).flatMap(value =>
        Array.isArray(value) ? value.map(String) : [String(value)],
    );
    return messages.length
        ? messages
        : ['The supply chain could not be saved.'];
};

// --- The schematic: a chain without the geography ---

const SCHEMATIC_BOX = Object.freeze({ width: 172, height: 38 });
const SCHEMATIC_GAP = Object.freeze({ x: 64, y: 12 });
const SCHEMATIC_HEADER = 26;

const shortenText = (text, length) =>
    text.length > length ? `${text.slice(0, length - 1)}…` : text;

// Where everything in a chain's schematic goes: its locations in columns,
// the start of the chain on the left, each column headed by its tier or
// step. Within a column, locations are ordered by where the locations they
// supply sit, to keep the lines from crossing.
export const getSchematicLayout = chain => {
    const { width: W, height: H } = SCHEMATIC_BOX;
    const columns = getChainGroups(chain);
    const rowOf = {};
    for (let k = columns.length - 1; k >= 0; k -= 1) {
        const rank = node =>
            Math.min(
                99,
                ...chain.links
                    .filter(([supplier]) => supplier === node.os_id)
                    .map(([, customer]) =>
                        rowOf[customer] === undefined ? 99 : rowOf[customer],
                    ),
            );
        columns[k].nodes = sortBy(columns[k].nodes, rank);
        columns[k].nodes.forEach((node, row) => {
            rowOf[node.os_id] = row;
        });
    }
    const rows = Math.max(...columns.map(column => column.nodes.length));
    const rowHeight = H + SCHEMATIC_GAP.y;

    const position = {};
    const boxes = [];
    columns.forEach((column, k) => {
        const x = k * (W + SCHEMATIC_GAP.x) + 2;
        const offset = ((rows - column.nodes.length) * rowHeight) / 2;
        column.nodes.forEach((node, row) => {
            const y = SCHEMATIC_HEADER + row * rowHeight + offset;
            position[node.os_id] = { x, y };
            const fullName = node.name || node.os_id;
            boxes.push({
                osId: node.os_id,
                x,
                y,
                fullName,
                name: shortenText(fullName, 25),
                sub: shortenText(
                    [node.stage, node.country_name].filter(Boolean).join(' · '),
                    30,
                ),
            });
        });
    });

    const edges = chain.links
        .filter(
            ([supplier, customer]) => position[supplier] && position[customer],
        )
        .map(([supplier, customer]) => {
            const from = position[supplier];
            const to = position[customer];
            const x1 = from.x + W;
            const y1 = from.y + H / 2;
            const x2 = to.x - 7;
            const y2 = to.y + H / 2;
            const middle = (x1 + x2) / 2;
            return {
                key: `${supplier}-${customer}`,
                d: `M${x1} ${y1} C${middle} ${y1} ${middle} ${y2} ${x2} ${y2}`,
            };
        });

    return {
        width: columns.length * W + (columns.length - 1) * SCHEMATIC_GAP.x + 4,
        height: rows * rowHeight + SCHEMATIC_HEADER + 4,
        box: SCHEMATIC_BOX,
        headers: columns.map((column, k) => ({
            label: column.label,
            x: k * (W + SCHEMATIC_GAP.x) + 2,
        })),
        boxes,
        edges,
    };
};

// Undo in the builder steps back through the chain's structure: which
// locations are in it and how they are linked. Text typed since (a name, what
// happens at a location) is kept.
export const chainStructureKey = chain =>
    JSON.stringify([chain.nodes.map(node => node.os_id), chain.links]);

export const restoreChainStructure = (chain, { nodes, links }) => {
    const current = {};
    chain.nodes.forEach(node => {
        current[node.os_id] = node;
    });
    return {
        ...chain,
        nodes: nodes.map(node => current[node.os_id] || node),
        links,
    };
};

// Whether the chain being edited differs from the one that was opened.
export const chainHasChanges = (draft, original) =>
    JSON.stringify(formatChainForAPI(draft)) !==
    JSON.stringify(formatChainForAPI(original));

// The chains with one moved up (-1) or down (1) a place.
export const moveChain = (chains, id, direction) => {
    const from = chains.findIndex(chain => chain.id === id);
    const to = from + direction;
    if (from < 0 || to < 0 || to >= chains.length) return chains;
    const moved = [...chains];
    moved.splice(to, 0, moved.splice(from, 1)[0]);
    return moved;
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
