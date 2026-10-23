import React from 'react';
import get from 'lodash/get';
import uniqBy from 'lodash/uniqBy';

import {
    STATUS_CLAIMED,
    STATUS_CROWDSOURCED,
    STATUS_MAPPED,
} from '../DataPoint/constants';
import { FIELD_CONFIG } from '../constants.jsx';
import IsicValue from './IsicValue';

/*
ISIC on the production location profile (OSDEV-3622): titles, never codes,
since the same number means different things across ISIC revisions and
national schemes. The profile shows the most specific level; the side panel
shows the full path. Values mapped from Location Type or Processing Type
(OSDEV-3382) come after submitted values and name what they came from.
*/

const LEVELS = ['section', 'division', 'group', 'class'];

// "C - Manufacturing" -> "Manufacturing", as extract_isic_code() reads it.
export const stripIsicCode = raw =>
    typeof raw === 'string'
        ? raw.replace(/^\s*(?:[A-Za-z]|\d+)\s*-\s+/, '')
        : '';

const pathKey = value => value.titles.join('\u0000');

const toSubmitted = item => {
    const raw = get(item, 'value.raw_value', item?.value);
    return (Array.isArray(raw) ? raw : [raw])
        .map(entry => LEVELS.map(level => stripIsicCode(entry?.[level])))
        .map(titles => ({
            titles: titles.filter(Boolean),
            sourceName: item.contributor_name || null,
            userId: item.contributor_id ?? undefined,
            date: item.created_at || null,
            provenance: item.provenance || null,
            statusLabel: item.is_from_claim
                ? STATUS_CLAIMED
                : STATUS_CROWDSOURCED,
        }));
};

// The app's font draws U+201D as the opening quote and U+201C as the
// closing one (see ContactInfoStep).
export const describeMappedSource = ({
    facility_type: facilityType,
    processing_type: processingType,
}) =>
    processingType && processingType !== facilityType
        ? `From Processing Type \u201D${processingType}\u201C`
        : `From Location Type \u201D${facilityType}\u201C`;

const toMapped = mappedValue => ({
    titles: mappedValue.path.map(step => step.title),
    sourceName: describeMappedSource(mappedValue),
    statusLabel: STATUS_MAPPED,
    isMapped: true,
});

// Side panel card: full path, and the badge, which on the profile itself
// sits in the status chip slot instead.
const toCard = value => ({
    value: (
        <IsicValue titles={value.titles} mapped={!!value.isMapped} showPath />
    ),
    sourceName: value.sourceName,
    date: value.date || null,
    userId: value.userId,
    provenance: value.provenance || null,
    isMapped: !!value.isMapped,
});

const getIsicDataPointProps = data => {
    if (!data) return null;
    // Each organization's value gets its own card; a mapped value only adds
    // a card for a path nobody submitted.
    const submitted = uniqBy(
        get(data, 'properties.extended_fields.isic_4', [])
            .flatMap(toSubmitted)
            .filter(value => value.titles.length),
        value => `${pathKey(value)}\u0000${value.sourceName}`,
    );
    const submittedPaths = new Set(submitted.map(pathKey));
    const mapped = uniqBy(
        get(data, 'properties.isic_4_mapped', [])
            .map(toMapped)
            .filter(value => !submittedPaths.has(pathKey(value))),
        pathKey,
    );
    const values = [...submitted, ...mapped];
    if (!values.length) return null;

    const [top, ...rest] = values;
    return {
        label: FIELD_CONFIG.isic_4.label,
        value: <IsicValue titles={top.titles} />,
        tooltipText: FIELD_CONFIG.isic_4.tooltipText,
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

export default getIsicDataPointProps;
