import get from 'lodash/get';
import maxBy from 'lodash/maxBy';
import uniqBy from 'lodash/uniqBy';

import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from '../DataPoint/constants';
import { FIELD_CONFIG } from '../constants.jsx';

/*
Industry Classification fields (OSDEV-3622): one per ISIC revision the
location has data under. Codes are shown, always inside their revision's
field, since the same code can mean different things in ISIC 4 and ISIC 5.
The profile shows the code and title of the level reported; the side panel
shows the full path. Open Supply Hub contributes ISIC 4 values mapped from
the location's Location Type and Processing Type (OSDEV-3382); they rank
after values organizations submitted.
*/

export const OPEN_SUPPLY_HUB = 'Open Supply Hub';
const LEVELS = ['section', 'division', 'group', 'class'];

// "C - Manufacturing" -> { code: 'C', title: 'Manufacturing' }
export const parseIsicLevel = raw => {
    if (typeof raw !== 'string' || !raw.trim()) return null;
    const match = /^\s*([A-Za-z]|\d+)\s*-\s+(.+)$/.exec(raw);
    return match
        ? { code: match[1].toUpperCase(), title: match[2].trim() }
        : { code: null, title: raw.trim() };
};

const formatStep = ({ code, title }) => (code ? `${code} · ${title}` : title);
export const formatLevel = path => formatStep(path[path.length - 1]);
export const formatPath = path => path.map(formatStep).join(' › ');
const pathKey = path => path.map(formatStep).join('\u0000');

const toSubmitted = item => {
    const raw = get(item, 'value.raw_value', item?.value);
    return (Array.isArray(raw) ? raw : [raw]).map(entry => ({
        path: LEVELS.map(level => parseIsicLevel(entry?.[level])).filter(
            Boolean,
        ),
        sourceName: item.contributor_name || null,
        userId: item.contributor_id ?? undefined,
        date: item.created_at || null,
        provenance: item.provenance || null,
        statusLabel: item.is_from_claim ? STATUS_CLAIMED : STATUS_CROWDSOURCED,
    }));
};

const submittedValues = (data, fieldName) =>
    uniqBy(
        get(data, `properties.extended_fields.${fieldName}`, [])
            .flatMap(toSubmitted)
            .filter(value => value.path.length),
        value => `${pathKey(value.path)}\u0000${value.sourceName}`,
    );

// Open Supply Hub's values date from the latest Location Type or Processing
// Type they were mapped from.
const mappedValues = data => {
    const sources = ['facility_type', 'processing_type'].flatMap(field =>
        get(data, `properties.extended_fields.${field}`, []),
    );
    const date = maxBy(sources, 'created_at')?.created_at ?? null;
    return uniqBy(
        get(data, 'properties.isic_4_mapped', [])
            .map(({ path }) => ({ path, sourceName: OPEN_SUPPLY_HUB, date }))
            .filter(value => value.path.length),
        value => pathKey(value.path),
    );
};

const toCard = value => ({
    value: formatPath(value.path),
    sourceName: value.sourceName,
    date: value.date || null,
    userId: value.userId,
    provenance: value.provenance || null,
});

const toField = (config, values) => {
    if (!values.length) return null;
    const [top, ...rest] = values;
    return {
        key: config.key,
        label: config.label,
        tooltipText: config.tooltipText,
        value: formatLevel(top.path),
        statusLabel: top.statusLabel,
        contributorName: top.sourceName,
        userId: top.userId,
        date: top.date || null,
        drawerData: {
            promotedContribution: toCard(top),
            contributions: rest.map(toCard),
        },
    };
};

const getIndustryClassificationFields = data =>
    data
        ? [
              toField(FIELD_CONFIG.isic_4, [
                  ...submittedValues(data, 'isic_4'),
                  ...mappedValues(data),
              ]),
              toField(FIELD_CONFIG.isic_5, submittedValues(data, 'isic_5')),
          ].filter(Boolean)
        : [];

export default getIndustryClassificationFields;
