import React from 'react';
import get from 'lodash/get';
import uniqBy from 'lodash/uniqBy';

import { STATUS_CLAIMED, STATUS_CROWDSOURCED } from '../DataPoint/constants';
import {
    FIELD_CONFIG,
    INDUSTRY_CLASSIFICATION_SECTION,
} from '../constants.jsx';
import IsicValue from './IsicValue';

/*
Industry Classification section of the production location profile
(OSDEV-3622): one field per scheme with contributor data (ISIC Rev. 4 for
now), then a separate "Mapped from OS Hub" field for ISIC values worked out
from Location Type or Processing Type (OSDEV-3382). Titles, never codes:
the field name says which scheme a value belongs to. The profile shows the
most specific level; the side panel shows the full path.
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
        ? `From Processing Type ”${processingType}“`
        : `From Location Type ”${facilityType}“`;

const toMapped = mappedValue => ({
    titles: mappedValue.path.map(step => step.title),
    sourceName: describeMappedSource(mappedValue),
    isMapped: true,
});

// Side panel card: the full path, and the badge on mapped values.
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

const toField = (config, values) => {
    if (!values.length) return null;
    const [top, ...rest] = values;
    // A mapped value names its source under the title, not as a person.
    const value = top.isMapped ? (
        <>
            <IsicValue titles={top.titles} />
            <span
                data-testid="isic-mapped-source"
                style={{ display: 'block', fontSize: '0.875rem' }}
            >
                {top.sourceName}
            </span>
        </>
    ) : (
        <IsicValue titles={top.titles} />
    );
    return {
        key: config.key,
        label: config.label,
        value,
        tooltipText: config.tooltipText,
        drawerFieldName: config.drawerFieldName,
        statusLabel: top.statusLabel,
        contributorName: top.isMapped ? null : top.sourceName,
        userId: top.userId,
        date: top.date || null,
        drawerData: {
            promotedContribution: toCard(top),
            contributions: rest.map(toCard),
        },
    };
};

const getIndustryClassificationGroup = data => {
    if (!data) return null;
    // Each organization's value gets its own card.
    const submitted = uniqBy(
        get(data, 'properties.extended_fields.isic_4', [])
            .flatMap(toSubmitted)
            .filter(value => value.titles.length),
        value => `${pathKey(value)}\u0000${value.sourceName}`,
    );
    const mapped = uniqBy(
        get(data, 'properties.isic_4_mapped', [])
            .map(toMapped)
            .filter(value => value.titles.length),
        pathKey,
    );
    const fields = [
        toField(FIELD_CONFIG.isic_4, submitted),
        toField(FIELD_CONFIG.isic_4_mapped, mapped),
    ].filter(Boolean);
    return fields.length
        ? { ...INDUSTRY_CLASSIFICATION_SECTION, fields }
        : null;
};

export default getIndustryClassificationGroup;
