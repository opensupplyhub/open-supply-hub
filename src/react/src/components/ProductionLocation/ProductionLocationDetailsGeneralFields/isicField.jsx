import React from 'react';
import get from 'lodash/get';
import uniqBy from 'lodash/uniqBy';
import { arrayOf, bool, string } from 'prop-types';
import Chip from '@material-ui/core/Chip';

import COLOURS from '../../../util/COLOURS';
import {
    STATUS_CLAIMED,
    STATUS_CROWDSOURCED,
    STATUS_MAPPED,
} from '../DataPoint/constants';
import { FIELD_CONFIG } from '../constants.jsx';

/*
ISIC on the production location profile (OSDEV-3622): titles, never codes,
since the same number means different things across ISIC revisions and
national schemes. The profile shows the most specific level; the side panel
shows the full path. Values mapped from Location Type or Processing Type
(OSDEV-3382) come after submitted values and name what they came from.
*/

const LEVELS = ['section', 'division', 'group', 'class'];
const SCHEME = 'ISIC 4';

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

export const describeMappedSource = ({
    facility_type: facilityType,
    processing_type: processingType,
}) =>
    processingType && processingType !== facilityType
        ? `From Processing Type "${processingType}"`
        : `From Location Type "${facilityType}"`;

const toMapped = mappedValue => ({
    titles: mappedValue.path.map(step => step.title),
    sourceName: describeMappedSource(mappedValue),
    statusLabel: STATUS_MAPPED,
    isMapped: true,
});

const chipStyle = (background, color, border = 'none') => ({
    background,
    color,
    border,
    borderRadius: 4,
    fontWeight: 600,
    marginLeft: 8,
});

export const IsicValue = ({ titles, mapped, showPath }) => (
    <span data-testid="isic-value">
        <span data-testid="isic-value-text">
            {showPath
                ? titles
                      .filter((title, i) => title !== titles[i - 1])
                      .join(' › ')
                : titles[titles.length - 1]}
        </span>
        <Chip
            label={SCHEME}
            size="small"
            style={chipStyle(COLOURS.VERSION_TAG_BG, COLOURS.VERSION_TAG_TEXT)}
            data-testid="isic-scheme-tag"
        />
        {mapped && (
            <Chip
                label={STATUS_MAPPED}
                size="small"
                style={chipStyle(
                    COLOURS.MAPPED_CHIP_BG,
                    COLOURS.MAPPED_CHIP_TEXT,
                    `1px dashed ${COLOURS.MAPPED_CHIP_BORDER}`,
                )}
                data-testid="isic-mapped-badge"
            />
        )}
    </span>
);

IsicValue.propTypes = {
    titles: arrayOf(string).isRequired,
    mapped: bool,
    showPath: bool,
};

IsicValue.defaultProps = { mapped: false, showPath: false };

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
