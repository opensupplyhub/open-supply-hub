import React, { useEffect, useRef, useState } from 'react';
import ReactDOM from 'react-dom';
import { arrayOf, bool, func, number, object, string } from 'prop-types';
import Button from '@material-ui/core/Button';
import Checkbox from '@material-ui/core/Checkbox';
import Chip from '@material-ui/core/Chip';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import COLOURS from '../util/COLOURS';
import { makeFacilityListCleaningDownloadURL } from '../util/util';

export const RUN_STATUS = Object.freeze({
    PENDING: 'PENDING',
    RUNNING: 'RUNNING',
    COMPLETE: 'COMPLETE',
    FAILED: 'FAILED',
});

export const KIND = Object.freeze({
    CORRECTION: 'CORRECTION',
    ISSUE: 'ISSUE',
    REMOVAL: 'REMOVAL',
});

export const DECISION = Object.freeze({
    PENDING: 'PENDING',
    ACCEPTED: 'ACCEPTED',
    REJECTED: 'REJECTED',
    EDITED: 'EDITED',
    REMOVED: 'REMOVED',
});

// Not a decision: a group action that clears the row-by-row decisions
// of that type so the ordinary group buttons cover every row again.
export const RESET = 'RESET';

export const isAuto = s => !!(s.extra && s.extra.auto);

export const SEVERITY = Object.freeze({
    MUST_FIX: 'must_fix',
    ADVISORY: 'advisory',
    INTERNAL_NOTE: 'internal_note',
});

/*
 * Which problems block approval and which are good to have. A flag a
 * human moderator would have to remove or send back (personal
 * information, a PO Box, a missing country) blocks; a suggested fix
 * (spacing, capitalisation) or something worth a look (one name at
 * several addresses) does not, and the contributor can prioritise.
 */
export const TIER = Object.freeze({
    BLOCKS: 'blocks',
    RECOMMENDED: 'recommended',
    AUTO: 'auto',
});

export const tierOf = group => {
    if (group.auto) return TIER.AUTO;
    if (group.severity === SEVERITY.MUST_FIX || group.kind === KIND.REMOVAL) {
        return TIER.BLOCKS;
    }
    return TIER.RECOMMENDED;
};

export const TIER_LABELS = Object.freeze({
    [TIER.BLOCKS]: 'Blocks approval',
    [TIER.RECOMMENDED]: 'Recommended',
    [TIER.AUTO]: 'Done automatically',
});

export const FIELD_LABELS = Object.freeze({
    country: 'Country',
    name: 'Name',
    address: 'Address',
    sector_product_type: 'Sector / product type',
    facility_type_processing_type: 'Facility type / processing type',
    number_of_workers: 'Number of workers',
    parent_company: 'Parent company',
    row: 'Row',
});

export const CODE_LABELS = Object.freeze({
    whitespace: 'extra spaces removed',
    quotes: 'stray quotes removed',
    filler_text: 'placeholder text removed',
    encoding: 'encoding fixed',
    country_code: 'country converted to its two-letter code',
    separators: 'separators standardised',
    workers_format: 'worker count formatted as a number',
    casing: 'capitalisation fixed',
    country_in_address: 'country name removed from the end of the address',
    name_in_address: 'facility name removed from the address',
    business_name_in_address: 'other business name removed from the address',
    duplicate: 'duplicate of another row',
    empty: 'blank row',
    pii: 'contains personal information',
    missing_country: 'country is missing',
    unknown_country: 'country not recognised',
    missing_name: 'facility name is missing',
    missing_address: 'address is missing',
    too_long: 'value is too long',
    address_po_box: 'address is a PO Box, not a street address',
    address_too_few: 'address has too little detail',
    name_incomplete: 'name looks incomplete',
    repeated_names: 'same name at several addresses',
    empty_row: 'blank row',
});

// What a contributor can do about each must-fix flag, in their words.
const CODE_HELP = Object.freeze({
    pii:
        'OS Hub does not publish personal names, email addresses or phone numbers. Edit the row to remove the personal details, or remove the row.',
    missing_country:
        'Every facility needs a country. Type the country, or remove the row.',
    unknown_country:
        'We could not match this country. Type the country name or its two-letter code, or remove the row.',
    missing_name:
        'Every facility needs a name. Type the facility name, or remove the row.',
    missing_address:
        'Every facility needs an address. Type the address, or remove the row.',
    too_long:
        'Shorten the value to 200 characters or fewer, or remove the row.',
    address_po_box:
        'A PO Box cannot be placed on the map. Type the street address, or remove the row.',
});

export const codeHelp = code => CODE_HELP[(code || '').split('+')[0]] || '';
/*
 * The guidance shown under a selected error type: what is wrong, why it
 * matters for everyone's data, and how to fix it. Wording follows the
 * data team's templated error messages.
 */
const GEOCODE_WHY =
    'OS Hub places every facility on a map and matches it against facilities other contributors have shared. A clear street address lets that happen accurately, so your facility is found, matched and counted correctly.';
const NAME_WHY =
    'Names are how OS Hub matches your facility with the same facility shared by others. A precise, unique name means your data merges with theirs instead of creating a duplicate or a wrong match.';
const CODE_GUIDE = Object.freeze({
    address_po_box: {
        title: 'PO Box in the address',
        problem:
            'The address appears to be a PO Box rather than the place where the facility is.',
        why: GEOCODE_WHY,
        fix: [
            'Replace the PO Box with the street address of the facility: street number (or cross streets, neighbourhood or industrial zone), town or city, state or province, and postal code if there is one.',
            'If you only have a PO Box, remove the row rather than publish a location that cannot be mapped.',
        ],
    },
    address_too_few: {
        title: 'Too little detail in the address',
        problem:
            'The address field contains too few details to locate the facility.',
        why: GEOCODE_WHY,
        fix: [
            'Make sure the address has a street number (or cross streets, neighbourhood or industrial zone) if available, town or city, state or province, and postal code where applicable.',
        ],
    },
    address_too_many: {
        title: 'Too much in the address',
        problem:
            'The address field contains details that are not part of the address.',
        why: GEOCODE_WHY,
        fix: [
            'Remove business names from the address field; they belong in the name or parent company column.',
            'Remove notes like "formerly located at" or "courtesy of", and local landmarks such as a police station.',
        ],
    },
    multiple_addresses: {
        title: 'More than one address in a row',
        problem:
            'The address field appears to hold the addresses of more than one location.',
        why: GEOCODE_WHY,
        fix: [
            'Give each location its own row, for example "Example Location - Building 1" and "Example Location - Building 3", each with its own address.',
            'Or, if you meant to include only one of them, remove the other address.',
        ],
    },
    address_split: {
        title: 'Address split across columns',
        problem: 'Parts of the address are in separate columns.',
        why: GEOCODE_WHY,
        fix: [
            'Put the whole address in one cell: street number, town or city, state or province and postal code together.',
        ],
    },
    country_mismatch: {
        title: 'Country does not match the address',
        problem: 'The country column and the country in the address disagree.',
        why:
            'The country decides which map region the facility is searched and matched in. A mismatch puts it in the wrong place or stops it matching at all.',
        fix: [
            'Change the country value to match the address, using the ISO country name or two-letter code. Hong Kong and Taiwan are listed as their own country values.',
        ],
    },
    unknown_country: {
        title: 'Country not recognised',
        problem: 'We could not match this value to a country.',
        why:
            'The country decides which map region the facility is searched and matched in, so every row needs one we can read.',
        fix: [
            'Type the country name as it appears in the ISO standard, or its two-letter code (for example VN or Viet Nam).',
        ],
    },
    missing_country: {
        title: 'Country is missing',
        problem: 'The country cell is empty.',
        why:
            'The country decides which map region the facility is searched and matched in; OS Hub cannot publish a facility without one.',
        fix: ['Type the country the facility is in, or remove the row.'],
    },
    missing_name: {
        title: 'Facility name is missing',
        problem: 'The name cell is empty.',
        why: NAME_WHY,
        fix: ['Type the facility name, or remove the row.'],
    },
    missing_address: {
        title: 'Address is missing',
        problem: 'The address cell is empty.',
        why: GEOCODE_WHY,
        fix: ['Type the street address of the facility, or remove the row.'],
    },
    name_incomplete: {
        title: 'Incomplete or generic name',
        problem:
            'The name is missing important details or is too general to identify one facility.',
        why: NAME_WHY,
        fix: [
            'Include the company name, the branch name if there is one, and the location if it helps tell sites apart.',
            'Avoid generic names like "Factory 1" or "China Office", or a city name with no company in it.',
        ],
    },
    name_too_many: {
        title: 'Too much in the name',
        problem:
            'The name field includes details that are not the facility name.',
        why: NAME_WHY,
        fix: [
            'Keep the company name, branch and location; remove "trading as", "t/a" and similar.',
            'If you want to record a company beyond the location name, put it in the parent company column.',
        ],
    },
    multiple_names: {
        title: 'More than one name in a row',
        problem: 'The name field appears to contain two names instead of one.',
        why: NAME_WHY,
        fix: [
            'If the second name is the parent company, move it to the parent company column.',
            'If they are two businesses at the same address, give each its own row with the same address.',
        ],
    },
    repeated_names: {
        title: 'Same name used for several locations',
        problem: 'Several rows share the same name at different addresses.',
        why:
            'When other contributors upload these facilities later, identical names lead to wrong matches between your sites. A distinguishing detail keeps each site separate.',
        fix: [
            'Give each site a unique name: the company name plus one distinguishing feature, such as "Example Factory - Weaving Unit", "Example Factory - Branch X" or "Example Factory - Name of Town".',
        ],
    },
    pii: {
        title: 'Personal information',
        problem:
            "This looks like an individual's name or personal contact details rather than a business.",
        why:
            "OS Hub does not publish individual people's names, email addresses or phone numbers, because doing so risks violating their privacy. Rows that contain them cannot be approved.",
        fix: [
            'Replace the personal details with the business name, or remove them from the row.',
            'If the value really is the business name, keep it and send confirming documentation to data@opensupplyhub.org.',
        ],
    },
    too_long: {
        title: 'Value is too long',
        problem: 'The value is over 200 characters.',
        why:
            'OS Hub stores names and addresses up to 200 characters; longer values are cut off, which can leave the facility unidentifiable.',
        fix: [
            'Shorten the value, keeping the parts that identify the facility.',
        ],
    },
    duplicate: {
        title: 'Duplicate rows',
        problem: 'Two rows have the same name and address.',
        why:
            'Only one version of a facility can exist on OS Hub; a duplicate would be matched to the first and discarded anyway.',
        fix: [
            'If they really are the same facility, nothing more is needed: the repeat is removed and the first row kept.',
            'If they are different facilities, keep the row and give it a unique unit number or address detail.',
        ],
    },
    empty: {
        title: 'Blank rows',
        problem: 'Every cell in the row is empty.',
        why: 'A blank row has nothing to publish.',
        fix: ['Nothing to do: the row is removed.'],
    },
    encoding: {
        title: 'Encoding or non-Roman characters',
        problem:
            'The value contains characters that are not in the Roman alphabet, or were mis-encoded (for example "OrlÃ©ans").',
        why:
            "Non-Roman and mis-encoded text does not match other contributors' spelling of the same facility, so it creates duplicates and fails searches.",
        fix: [
            'Use the Roman or English equivalent, for example Hyderabad; keep accents only where your file encodes them correctly, otherwise drop them (Orleans).',
        ],
    },
    separators: {
        title: 'Separators standardised',
        problem:
            'Several values in one cell were separated by something other than a vertical bar or a comma.',
        why:
            'OS Hub reads "Apparel|Shirts|Jackets" as three values; "Apparel / Shirts / Jackets" would be read as one unknown value.',
        fix: [
            'Separate values with a vertical bar (|) or a comma in the sector, product type, facility type and parent company columns.',
        ],
    },
    sector_values: {
        title: 'Values in the wrong column',
        problem:
            'Facility or processing types appear under sector or product type, or the other way round, or do not match the supported values.',
        why:
            'These columns feed the filters on OS Hub; values in the wrong column or outside the supported list cannot be searched.',
        fix: [
            'Put products and sectors under sector_product_type and activities under facility_type_processing_type.',
            'Choose from the supported sector values.',
        ],
    },
    spelling: {
        title: 'Spelling',
        problem: 'A value is misspelt, for example "Manufactoring".',
        why:
            "Misspelt values do not match the supported taxonomy or other contributors' entries.",
        fix: ['Correct the spelling.'],
    },
    filler_text: {
        title: 'Placeholder text removed',
        problem:
            'A cell held filler such as "N/A", "None" or "-" instead of being left empty.',
        why:
            'Only country, name and address are required; everything else should be blank when unknown, or the placeholder is published as if it were data.',
        fix: [
            'Leave the cell empty; the placeholder has been removed for you.',
        ],
    },
    workers_format: {
        title: 'Worker count formatted as a number',
        problem: 'The number of workers contained symbols or commas.',
        why:
            'OS Hub reads "2,100" as two numbers (2 and 100). Only plain numbers and ranges like 200-500 are understood.',
        fix: [
            'Use a plain number or a range with a dash; the value has been reformatted for you.',
        ],
    },
    country_code: {
        title: 'Country converted to its code',
        problem: 'The country was written as a name.',
        why:
            "OS Hub stores the ISO two-letter code so every contributor's facilities line up by country.",
        fix: ['Nothing to do; the code has been filled in for you.'],
    },
    whitespace: {
        title: 'Extra spaces removed',
        problem: 'The value had leading, trailing or doubled spaces.',
        why:
            "Stray spaces stop values matching other contributors' spelling of the same name or address.",
        fix: ['Nothing to do; the spaces have been trimmed for you.'],
    },
    casing: {
        title: 'Capitalisation fixed',
        problem: 'The name was in all capitals.',
        why:
            "Names are published as written; consistent capitalisation reads better and matches other contributors' entries.",
        fix: [
            'Nothing to do; the name has been recased for you. Keep the original if the company writes it in capitals.',
        ],
    },
    quotes: {
        title: 'Stray quotes removed',
        problem: 'The value was wrapped in or contained stray quotation marks.',
        why:
            'Quotation marks become part of the published value and break matching.',
        fix: ['Nothing to do; they have been removed for you.'],
    },
    country_in_address: {
        title: 'Country removed from the end of the address',
        problem:
            'The address ended with the country name, which is already in the country column.',
        why:
            'The geocoder works best with the address alone; the country is supplied separately.',
        fix: [
            'Accept the trimmed address, or keep the original if the country is part of a place name.',
        ],
    },
});

export const codeGuide = code => CODE_GUIDE[(code || '').split('+')[0]] || null;

export const styles = Object.freeze({
    panel: Object.freeze({
        padding: '20px',
        margin: '0 0.5rem 20px 0.5rem',
    }),
    heading: Object.freeze({
        fontSize: '1.25rem',
        fontWeight: 700,
        marginBottom: '8px',
    }),
    muted: Object.freeze({
        color: 'rgba(0, 0, 0, 0.6)',
    }),
    statRow: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        gap: '12px',
        margin: '16px 0',
    }),
    stat: Object.freeze({
        flex: '1 1 160px',
        padding: '12px 16px',
        borderRadius: '4px',
        background: '#F5F5F5',
    }),
    statNumber: Object.freeze({
        fontSize: '1.6rem',
        fontWeight: 700,
        lineHeight: 1.2,
    }),
    statLabel: Object.freeze({
        fontSize: '0.8rem',
        color: 'rgba(0, 0, 0, 0.6)',
    }),
    disclaimer: Object.freeze({
        padding: '12px 16px',
        margin: '12px 0',
        borderLeft: `4px solid ${COLOURS.NAVY_BLUE}`,
        background: '#F0F4FF',
        fontSize: '0.9rem',
    }),
    rowCard: Object.freeze({
        border: '1px solid #E0E0E0',
        borderRadius: '4px',
        padding: '12px 16px',
        marginBottom: '12px',
    }),
    rowHeader: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'baseline',
        gap: '12px',
        marginBottom: '8px',
    }),
    rowCheckbox: Object.freeze({
        padding: '0 4px 0 0',
        margin: '-4px 0 -4px -8px',
        alignSelf: 'center',
    }),
    bulkBar: Object.freeze({
        position: 'sticky',
        top: '48px', // below the compact readiness bar
        zIndex: 2,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 12px',
        margin: '0 0 12px 0',
        background: '#F5F0FF',
        border: '1px solid #CBB4F5',
        borderRadius: '4px',
    }),
    bulkCount: Object.freeze({
        fontWeight: 700,
        marginRight: '4px',
    }),
    selectAll: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        gap: '2px',
        margin: '0 0 4px -8px',
        fontSize: '0.9rem',
        color: 'rgba(0, 0, 0, 0.7)',
    }),
    rowNumber: Object.freeze({
        fontWeight: 700,
        whiteSpace: 'nowrap',
    }),
    rowIdentity: Object.freeze({
        color: 'rgba(0, 0, 0, 0.7)',
        overflowWrap: 'anywhere',
    }),
    suggestion: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '8px 16px',
        padding: '8px 0',
        borderTop: '1px solid #F0F0F0',
    }),
    tag: Object.freeze({
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '10px',
        fontSize: '0.75rem',
        fontWeight: 700,
        whiteSpace: 'nowrap',
    }),
    mustFixTag: Object.freeze({
        background: '#FDECEA',
        color: '#B3261E',
    }),
    internalTag: Object.freeze({
        background: '#EEEEEE',
        color: '#424242',
    }),
    correctionTag: Object.freeze({
        background: '#E8F5E9',
        color: '#1B5E20',
    }),
    removalTag: Object.freeze({
        background: '#FFF3E0',
        color: '#E65100',
    }),
    valueBlock: Object.freeze({
        flex: '1 1 260px',
        minWidth: 0,
    }),
    fieldName: Object.freeze({
        fontSize: '0.8rem',
        color: 'rgba(0, 0, 0, 0.6)',
    }),
    original: Object.freeze({
        textDecoration: 'line-through',
        color: 'rgba(0, 0, 0, 0.5)',
        overflowWrap: 'anywhere',
    }),
    corrected: Object.freeze({
        fontWeight: 600,
        overflowWrap: 'anywhere',
    }),
    arrow: Object.freeze({
        margin: '0 8px',
        color: 'rgba(0, 0, 0, 0.4)',
    }),
    decisionBlock: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        marginLeft: 'auto',
    }),
    decisionText: Object.freeze({
        fontSize: '0.85rem',
        fontWeight: 600,
        marginRight: '8px',
    }),
    footer: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '12px',
        marginTop: '16px',
    }),
    error: Object.freeze({
        color: 'red',
    }),
    headerIssues: Object.freeze({
        margin: '4px 0 12px 0',
        padding: '8px 12px',
        borderLeft: '4px solid #d32f2f',
        background: '#FFF4F2',
    }),
});

export const describeCode = code =>
    (code || '')
        .split('+')
        .map(part => CODE_LABELS[part] || part.replace(/_/g, ' '))
        .join(', ');

export const fieldLabel = field => FIELD_LABELS[field] || field;

export const Tag = ({ style, children }) => (
    <span style={{ ...styles.tag, ...style }}>{children}</span>
);

Tag.propTypes = { style: object.isRequired, children: string.isRequired };

export const Stat = ({ value, label }) => (
    <div style={styles.stat}>
        <div style={styles.statNumber}>{value}</div>
        <div style={styles.statLabel}>{label}</div>
    </div>
);

Stat.propTypes = { value: number.isRequired, label: string.isRequired };

const plural = (n, word, words = `${word}s`) =>
    `${n} ${n === 1 ? word : words}`;

const trackerStyles = Object.freeze({
    box: Object.freeze({
        margin: '16px 0',
        padding: '16px 20px',
        borderRadius: '6px',
        background: '#F5F0FF',
        border: '1px solid #E2D1F0',
    }),
    headline: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'baseline',
        justifyContent: 'space-between',
        gap: '8px',
        marginBottom: '8px',
    }),
    title: Object.freeze({
        fontSize: '1.15rem',
        fontWeight: 700,
    }),
    percent: Object.freeze({
        fontSize: '1.6rem',
        fontWeight: 800,
        lineHeight: 1,
    }),
    track: Object.freeze({
        height: '12px',
        borderRadius: '6px',
        background: '#E2D9F3',
        overflow: 'hidden',
    }),
    fill: Object.freeze({
        height: '100%',
        borderRadius: '6px',
        transition: 'width .5s ease, background .5s ease',
    }),
    figures: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        margin: '12px 0 0 0',
        fontSize: '0.95rem',
    }),
    figure: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '4px 12px',
    }),
    viewFixes: Object.freeze({
        padding: '2px 8px',
        minHeight: 0,
        fontSize: '0.8rem',
    }),
    // A zero-height sticky anchor: it takes no room in the flow, sticks
    // to the top of the scrolling area, and the compact bar hangs off it
    // so nothing jumps when the bar appears.
    stickyAnchor: Object.freeze({
        position: 'sticky',
        top: 0,
        height: 0,
        zIndex: 3,
        overflow: 'visible',
    }),
    compact: Object.freeze({
        position: 'absolute',
        left: '-16px',
        right: '-16px',
        top: 0,
        height: '44px',
        display: 'flex',
        alignItems: 'center',
        gap: '14px',
        padding: '0 16px',
        background: 'rgba(255, 255, 255, 0.97)',
        borderBottom: '1px solid #E2D1F0',
        boxShadow: '0 2px 6px rgba(0, 0, 0, 0.08)',
        fontSize: '0.9rem',
        transition: 'opacity .2s',
    }),
    compactTitle: Object.freeze({
        fontWeight: 700,
        whiteSpace: 'nowrap',
    }),
    compactTrack: Object.freeze({
        flex: '1 1 120px',
        height: '8px',
        borderRadius: '4px',
        background: '#E2D9F3',
        overflow: 'hidden',
    }),
    compactMeta: Object.freeze({
        whiteSpace: 'nowrap',
        color: 'rgba(0, 0, 0, 0.65)',
    }),
});

const PURPLE = '#8428FA';
const GREEN = COLOURS.MATERIAL_GREEN;

/*
 * One bar and one number: how many rows still wait for the contributor
 * before the list is ready to submit for human review. Rows are the
 * unit everywhere on the screen, so this agrees with the chips. The
 * automatic fixes are already decided, so the bar never opens at zero;
 * they get one line here with a way to open them, and nowhere else.
 */
export const ReadinessTracker = ({
    summary,
    applied,
    fixed,
    showingAuto,
    onViewFixes,
}) => {
    const total = summary.rows_to_review || 0;
    const pending = summary.rows_pending_review || 0;
    const done = total - pending;
    const percent = total ? Math.round((100 * done) / total) : 100;
    const ready = pending === 0;
    const blocking = summary.rows_blocking_pending || 0;
    const recommended = summary.rows_recommended_pending || 0;
    const auto = summary.auto_fixes || 0;
    const autoRows = summary.auto_rows || 0;

    // Once the full box scrolls out of view a one-line version of it
    // sticks to the top, so the bar is always in sight.
    const boxRef = useRef(null);
    const [compact, setCompact] = useState(false);
    // On the list page an ancestor has overflow:auto without scrolling,
    // which defeats position:sticky, so there the bar is fixed instead:
    // pinned under the site header and sized to the panel.
    const [pinned, setPinned] = useState(null);
    useEffect(() => {
        if (!boxRef.current || typeof IntersectionObserver === 'undefined') {
            return undefined;
        }
        const measure = () => {
            if (!fixed || !boxRef.current) return;
            const r = boxRef.current.getBoundingClientRect();
            const header = document.querySelector('header');
            const headerBottom = header
                ? header.getBoundingClientRect().bottom
                : 0;
            setPinned({
                left: r.left,
                width: r.width,
                top: Math.max(0, headerBottom),
            });
        };
        const observer = new IntersectionObserver(
            ([entry]) => {
                const hidden =
                    !entry.isIntersecting && entry.boundingClientRect.top < 0;
                if (hidden) measure();
                setCompact(hidden);
            },
            { threshold: 0 },
        );
        observer.observe(boxRef.current);
        window.addEventListener('resize', measure);
        return () => {
            observer.disconnect();
            window.removeEventListener('resize', measure);
        };
    }, [fixed]);
    const anchorStyle =
        fixed && pinned
            ? {
                  ...trackerStyles.stickyAnchor,
                  position: 'fixed',
                  top: `${pinned.top}px`,
                  left: `${pinned.left}px`,
                  width: `${pinned.width}px`,
              }
            : trackerStyles.stickyAnchor;
    const compactEdges = fixed ? { left: 0, right: 0 } : {};

    let title;
    if (ready && summary.changes_unapplied > 0) {
        title = 'Review done: submit your list for human review';
    } else if (ready) {
        title = applied ? 'Submitted for human review' : 'Review done';
    } else {
        title = `Your review is ${percent}% done`;
    }

    const colour = ready ? GREEN : PURPLE;
    let shortTitle = `${percent}% of your review done`;
    if (ready) {
        shortTitle =
            summary.changes_unapplied > 0
                ? 'Review done: press Submit'
                : 'Review done';
    }
    const split = [];
    if (blocking > 0) {
        split.push(`${plural(blocking, 'row')} block approval`);
    }
    if (recommended > 0) {
        split.push(
            `${recommended} with recommended fixes${
                blocking > 0 ? ' only' : ''
            }`,
        );
    }

    const anchor = (
        <div style={anchorStyle} aria-hidden={!compact}>
            <div
                style={{
                    ...trackerStyles.compact,
                    ...compactEdges,
                    opacity: compact ? 1 : 0,
                    pointerEvents: compact ? 'auto' : 'none',
                }}
                data-tour="compact"
            >
                <span style={{ ...trackerStyles.compactTitle, color: colour }}>
                    {shortTitle}
                </span>
                <div style={trackerStyles.compactTrack}>
                    <div
                        style={{
                            ...trackerStyles.fill,
                            width: `${percent}%`,
                            background: colour,
                        }}
                    />
                </div>
                <span style={trackerStyles.compactMeta}>
                    {ready
                        ? `${plural(total, 'row')} reviewed`
                        : `${plural(pending, 'row')} to go${
                              blocking > 0
                                  ? ` · ${blocking} block approval`
                                  : ''
                          }`}
                </span>
            </div>
        </div>
    );
    // An ancestor of the list-page panel has a transform, which makes
    // position:fixed relative to it; a portal onto the body avoids that.
    const bar =
        fixed && pinned && typeof document !== 'undefined'
            ? ReactDOM.createPortal(anchor, document.body)
            : anchor;

    return (
        <>
            <div style={trackerStyles.box} data-tour="intro" ref={boxRef}>
                <div style={trackerStyles.headline}>
                    <span style={trackerStyles.title}>{title}</span>
                    <span
                        style={{
                            ...trackerStyles.percent,
                            color: ready ? GREEN : PURPLE,
                        }}
                    >
                        {percent}%
                    </span>
                </div>
                <div
                    style={trackerStyles.track}
                    role="progressbar"
                    aria-valuenow={percent}
                    aria-valuemin={0}
                    aria-valuemax={100}
                >
                    <div
                        style={{
                            ...trackerStyles.fill,
                            width: `${percent}%`,
                            background: ready ? GREEN : PURPLE,
                        }}
                    />
                </div>
                <div style={trackerStyles.figures}>
                    <div style={trackerStyles.figure}>
                        {ready ? (
                            <span>
                                <b>{plural(total, 'row')}</b> reviewed. Nothing
                                else needs your decision.
                            </span>
                        ) : (
                            <span>
                                <b>{plural(pending, 'row')}</b>{' '}
                                {pending === 1 ? 'still needs' : 'still need'}{' '}
                                your review
                                {split.length > 0 && `: ${split.join(' · ')}`}.
                            </span>
                        )}
                    </div>
                    {auto > 0 && (
                        <div style={trackerStyles.figure} data-tour="automatic">
                            <span>
                                <b>
                                    {plural(
                                        auto,
                                        'formatting fix',
                                        'formatting fixes',
                                    )}
                                </b>{' '}
                                will be made automatically on{' '}
                                {plural(autoRows, 'row')} when you submit.
                            </span>
                            {onViewFixes && (
                                <Button
                                    size="small"
                                    color="primary"
                                    style={trackerStyles.viewFixes}
                                    onClick={onViewFixes}
                                >
                                    {showingAuto ? 'Hide fixes' : 'View fixes'}
                                </Button>
                            )}
                        </div>
                    )}
                </div>
            </div>
            {bar}
        </>
    );
};

ReadinessTracker.defaultProps = {
    applied: false,
    fixed: false,
    showingAuto: false,
    onViewFixes: null,
};
ReadinessTracker.propTypes = {
    summary: object.isRequired,
    applied: bool,
    fixed: bool,
    showingAuto: bool,
    onViewFixes: func,
};

export const Correction = ({ suggestion, canAct, busy, onDecide }) => {
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState(
        suggestion.decided_value || suggestion.corrected_value,
    );
    const finalValue =
        suggestion.decision === DECISION.EDITED
            ? suggestion.decided_value
            : suggestion.corrected_value;

    const decisionLabel = (() => {
        switch (suggestion.decision) {
            case DECISION.ACCEPTED:
                if (suggestion.applied) return 'Applied';
                return isAuto(suggestion) ? 'Accepted (automatic)' : 'Accepted';
            case DECISION.EDITED:
                return suggestion.applied ? 'Applied (edited)' : 'Edited';
            case DECISION.REJECTED:
                return 'Kept original';
            case DECISION.REMOVED:
                return 'Row will be removed';
            default:
                return 'Needs your decision';
        }
    })();

    return (
        <div style={styles.suggestion}>
            <Tag style={styles.correctionTag}>Suggested fix</Tag>
            <div style={styles.valueBlock}>
                <div style={styles.fieldName}>
                    {fieldLabel(suggestion.field)}:{' '}
                    {describeCode(suggestion.code)}
                </div>
                {editing ? (
                    <TextField
                        value={draft}
                        onChange={e => setDraft(e.target.value)}
                        fullWidth
                        margin="dense"
                        autoFocus
                    />
                ) : (
                    <div>
                        <span style={styles.original}>
                            {suggestion.original_value || '(blank)'}
                        </span>
                        <span style={styles.arrow}>&rarr;</span>
                        <span style={styles.corrected}>
                            {finalValue || '(blank)'}
                        </span>
                    </div>
                )}
                {suggestion.note && (
                    <div style={styles.muted}>{suggestion.note}</div>
                )}
            </div>
            <div style={styles.decisionBlock}>
                <span style={styles.decisionText}>{decisionLabel}</span>
                {canAct && editing && (
                    <>
                        <Button
                            size="small"
                            color="primary"
                            disabled={busy || !draft}
                            onClick={() => {
                                setEditing(false);
                                onDecide(DECISION.EDITED, draft);
                            }}
                        >
                            Save
                        </Button>
                        <Button
                            size="small"
                            disabled={busy}
                            onClick={() => setEditing(false)}
                        >
                            Cancel
                        </Button>
                    </>
                )}
                {canAct && !editing && (
                    <>
                        {suggestion.decision !== DECISION.ACCEPTED && (
                            <Button
                                size="small"
                                color="primary"
                                disabled={busy}
                                onClick={() => onDecide(DECISION.ACCEPTED)}
                            >
                                Accept
                            </Button>
                        )}
                        {suggestion.decision !== DECISION.REJECTED && (
                            <Button
                                size="small"
                                disabled={busy}
                                onClick={() => onDecide(DECISION.REJECTED)}
                            >
                                Keep original
                            </Button>
                        )}
                        <Button
                            size="small"
                            disabled={busy}
                            onClick={() => setEditing(true)}
                        >
                            Edit
                        </Button>
                    </>
                )}
            </div>
        </div>
    );
};

Correction.propTypes = {
    suggestion: object.isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    onDecide: func.isRequired,
};

export const Issue = ({ suggestion, canAct, busy, onDecide }) => {
    const internal = suggestion.severity === SEVERITY.INTERNAL_NOTE;
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState(
        suggestion.decided_value || suggestion.original_value || '',
    );
    const editable =
        !internal && suggestion.field && suggestion.field !== 'row';

    const decisionLabel = (() => {
        switch (suggestion.decision) {
            case DECISION.EDITED:
                return suggestion.applied ? 'Fixed' : 'Fixed (not yet applied)';
            case DECISION.REMOVED:
                return 'Row will be removed';
            case DECISION.REJECTED:
                return 'Left as uploaded';
            default:
                return internal ? '' : 'Needs your attention';
        }
    })();

    return (
        <div style={styles.suggestion}>
            <Tag style={internal ? styles.internalTag : styles.mustFixTag}>
                {internal ? 'Moderator note' : 'Needs your attention'}
            </Tag>
            <div style={styles.valueBlock}>
                <div style={styles.fieldName}>
                    {fieldLabel(suggestion.field)}:{' '}
                    {describeCode(suggestion.code)}
                </div>
                {editing ? (
                    <TextField
                        value={draft}
                        onChange={e => setDraft(e.target.value)}
                        fullWidth
                        margin="dense"
                        autoFocus
                    />
                ) : (
                    <div>
                        {suggestion.decision === DECISION.EDITED ? (
                            <>
                                <span style={styles.original}>
                                    {suggestion.original_value || '(blank)'}
                                </span>
                                <span style={styles.arrow}>&rarr;</span>
                                <span style={styles.corrected}>
                                    {suggestion.decided_value}
                                </span>
                            </>
                        ) : (
                            <span>
                                {suggestion.original_value || '(blank)'}
                            </span>
                        )}
                    </div>
                )}
                <div style={styles.muted}>{suggestion.note}</div>
                {!internal && codeHelp(suggestion.code) && (
                    <div style={styles.muted}>{codeHelp(suggestion.code)}</div>
                )}
            </div>
            <div style={styles.decisionBlock}>
                <span style={styles.decisionText}>{decisionLabel}</span>
                {canAct && !internal && editing && (
                    <>
                        <Button
                            size="small"
                            color="primary"
                            disabled={busy || !draft}
                            onClick={() => {
                                setEditing(false);
                                onDecide(DECISION.EDITED, draft);
                            }}
                        >
                            Save
                        </Button>
                        <Button
                            size="small"
                            disabled={busy}
                            onClick={() => setEditing(false)}
                        >
                            Cancel
                        </Button>
                    </>
                )}
                {canAct && !internal && !editing && (
                    <>
                        {editable && (
                            <Button
                                size="small"
                                color="primary"
                                disabled={busy}
                                onClick={() => setEditing(true)}
                            >
                                Fix value
                            </Button>
                        )}
                        {suggestion.decision !== DECISION.REMOVED && (
                            <Button
                                size="small"
                                color="secondary"
                                disabled={busy}
                                onClick={() => onDecide(DECISION.REMOVED)}
                            >
                                Remove row
                            </Button>
                        )}
                        {suggestion.decision !== DECISION.REJECTED &&
                            suggestion.decision !== DECISION.PENDING && (
                                <Button
                                    size="small"
                                    disabled={busy}
                                    onClick={() => onDecide(DECISION.REJECTED)}
                                >
                                    Undo
                                </Button>
                            )}
                    </>
                )}
            </div>
        </div>
    );
};

Issue.defaultProps = { canAct: false, busy: false, onDecide: () => {} };

Issue.propTypes = {
    suggestion: object.isRequired,
    canAct: bool,
    busy: bool,
    onDecide: func,
};

export const Removal = ({ suggestion, canAct, busy, onDecide }) => {
    const decisionLabel = (() => {
        switch (suggestion.decision) {
            case DECISION.ACCEPTED:
                return suggestion.applied ? 'Removed' : 'Will be removed';
            case DECISION.REJECTED:
                return 'Kept';
            case DECISION.REMOVED:
                return 'Will be removed';
            default:
                return 'Needs your decision';
        }
    })();
    return (
        <div style={styles.suggestion}>
            <Tag style={styles.removalTag}>Suggested removal</Tag>
            <div style={styles.valueBlock}>
                <div style={styles.fieldName}>
                    {describeCode(suggestion.code)}
                </div>
                <div>{suggestion.note}</div>
            </div>
            <div style={styles.decisionBlock}>
                <span style={styles.decisionText}>{decisionLabel}</span>
                {canAct && suggestion.decision !== DECISION.ACCEPTED && (
                    <Button
                        size="small"
                        color="primary"
                        disabled={busy}
                        onClick={() => onDecide(DECISION.ACCEPTED)}
                    >
                        Remove row
                    </Button>
                )}
                {canAct && suggestion.decision !== DECISION.REJECTED && (
                    <Button
                        size="small"
                        disabled={busy}
                        onClick={() => onDecide(DECISION.REJECTED)}
                    >
                        Keep row
                    </Button>
                )}
            </div>
        </div>
    );
};

Removal.propTypes = {
    suggestion: object.isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    onDecide: func.isRequired,
};

/*
 * Whole-file findings. Exact duplicates are an automatic group and
 * repeated names an advisory one, so both live in the chips; only a
 * header problem, which has no rows to act on, is left to say here.
 */
export const ListFindings = ({ filePass }) => {
    const headerIssues = filePass.header_issues || [];
    if (!headerIssues.length) return null;
    return (
        <div style={styles.headerIssues}>
            {headerIssues.map(issue => (
                <div key={`header-${issue.column || issue.note}`}>
                    {issue.note || `Header problem: ${issue.column}`}
                </div>
            ))}
        </div>
    );
};

ListFindings.propTypes = { filePass: object.isRequired };

export const suggestionKey = s => `${s.kind}:${s.code}:${s.field}`;

export const visibleRows = (rows, filter) =>
    rows
        .map(row =>
            filter
                ? { ...row, suggestions: row.suggestions.filter(filter) }
                : row,
        )
        .filter(row => row.suggestions.length);

export const SuggestionRows = ({
    rows,
    canAct,
    busy,
    decide,
    filter,
    selected,
    onToggle,
}) =>
    visibleRows(rows, filter).map((row, i) => (
        <div
            key={row.row_number}
            style={styles.rowCard}
            data-tour={i === 0 ? 'rows' : undefined}
        >
            <div style={styles.rowHeader}>
                {canAct && onToggle && (
                    <Checkbox
                        checked={selected.has(row.row_number)}
                        onChange={() => onToggle(row.row_number)}
                        disabled={busy}
                        color="primary"
                        style={styles.rowCheckbox}
                        inputProps={{
                            'aria-label': `Select row ${row.row_number}`,
                        }}
                    />
                )}
                <span style={styles.rowNumber}>Row {row.row_number}</span>
                <span style={styles.rowIdentity}>
                    {row.name}
                    {row.address ? ` — ${row.address}` : ''}
                    {row.country_code ? ` (${row.country_code})` : ''}
                </span>
            </div>
            {row.suggestions.map(suggestion => {
                const onDecide = (decision, value) =>
                    decide([{ id: suggestion.id, decision, value }]);
                if (suggestion.kind === KIND.CORRECTION) {
                    return (
                        <Correction
                            key={suggestion.id}
                            suggestion={suggestion}
                            canAct={canAct}
                            busy={busy}
                            onDecide={onDecide}
                        />
                    );
                }
                if (suggestion.kind === KIND.REMOVAL) {
                    return (
                        <Removal
                            key={suggestion.id}
                            suggestion={suggestion}
                            canAct={canAct}
                            busy={busy}
                            onDecide={onDecide}
                        />
                    );
                }
                return (
                    <Issue
                        key={suggestion.id}
                        suggestion={suggestion}
                        canAct={canAct}
                        busy={busy}
                        onDecide={onDecide}
                    />
                );
            })}
        </div>
    ));

SuggestionRows.defaultProps = {
    filter: null,
    selected: new Set(),
    onToggle: null,
};

SuggestionRows.propTypes = {
    rows: arrayOf(object).isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decide: func.isRequired,
    filter: func,
    selected: object,
    onToggle: func,
};

const groupTitle = group => {
    if (group.kind === KIND.REMOVAL) {
        return `Rows to remove: ${describeCode(group.code)}`;
    }
    return `${fieldLabel(group.field)}: ${describeCode(group.code)}`;
};

const groupStatus = group => {
    const parts = [];
    if (group.pending) parts.push(`${group.pending} to review`);
    if (group.accepted) {
        parts.push(
            group.kind === KIND.REMOVAL
                ? `${group.accepted} to remove`
                : `${group.accepted} accepted`,
        );
    }
    if (group.edited) parts.push(`${group.edited} fixed by you`);
    if (group.removed) parts.push(`${plural(group.removed, 'row')} to remove`);
    if (group.rejected) parts.push(`${group.rejected} kept as uploaded`);
    if (group.applied) parts.push(`${group.applied} applied`);
    return parts.join(' · ');
};

const ALL = 'all';

const chipStyles = Object.freeze({
    tiers: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        padding: '4px 0 12px 0',
        borderBottom: `1px solid ${COLOURS.GREY}`,
        marginBottom: '12px',
    }),
    tier: Object.freeze({
        display: 'grid',
        gridTemplateColumns: '118px 1fr',
        alignItems: 'center',
        gap: '8px',
    }),
    tierChips: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '8px',
        minWidth: 0,
    }),
    tierLabel: Object.freeze({
        fontSize: '0.75rem',
        fontWeight: 700,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        textAlign: 'right',
    }),
    dot: Object.freeze({
        display: 'inline-block',
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        marginRight: '6px',
    }),
    header: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
        padding: '0 0 12px 0',
    }),
    headerActions: Object.freeze({
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        alignItems: 'center',
    }),
});

const ADVISORY_COLOUR = '#f9a825';

const groupKindColour = group => {
    if (group.severity === SEVERITY.INTERNAL_NOTE || group.auto) {
        return COLOURS.DARK_GREY;
    }
    if (group.severity === SEVERITY.ADVISORY) return ADVISORY_COLOUR;
    if (group.kind === KIND.ISSUE) return '#d32f2f';
    if (group.kind === KIND.REMOVAL) return '#ef6c00';
    return '#2e7d32';
};

const chipLabel = group => (
    <span>
        <span
            style={{ ...chipStyles.dot, background: groupKindColour(group) }}
        />
        {groupTitle(group)} ({group.count})
    </span>
);

const guideStyles = Object.freeze({
    box: Object.freeze({
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
        gap: '8px 24px',
        padding: '14px 18px',
        margin: '4px 0 8px 0',
        borderRadius: '6px',
        background: '#FFF8E6',
        borderLeftWidth: '4px',
        borderLeftStyle: 'solid',
        borderLeftColor: '#f57c00',
    }),
    boxAuto: Object.freeze({
        background: COLOURS.LIGHT_GREY,
        borderLeftColor: COLOURS.DARK_GREY,
    }),
    boxFix: Object.freeze({
        background: '#F1F8F1',
        borderLeftColor: '#2e7d32',
    }),
    title: Object.freeze({
        gridColumn: '1 / -1',
        fontSize: '1.05rem',
        fontWeight: 700,
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '6px 10px',
    }),
    badge: Object.freeze({
        display: 'inline-block',
        padding: '2px 8px',
        borderRadius: '10px',
        fontSize: '0.7rem',
        fontWeight: 700,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        color: COLOURS.WHITE,
        whiteSpace: 'nowrap',
    }),
    label: Object.freeze({
        fontSize: '0.75rem',
        fontWeight: 700,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        color: 'rgba(0, 0, 0, 0.6)',
        margin: '0 0 2px 0',
    }),
    list: Object.freeze({
        margin: '0',
        padding: '0 0 0 18px',
    }),
    example: Object.freeze({
        gridColumn: '1 / -1',
        fontSize: '0.9rem',
        color: 'rgba(0, 0, 0, 0.7)',
    }),
});

const TIER_COLOURS = Object.freeze({
    [TIER.BLOCKS]: '#d32f2f',
    [TIER.RECOMMENDED]: '#2e7d32',
    [TIER.AUTO]: COLOURS.DARK_GREY,
});

const TierBadge = ({ tier, advisory }) => (
    <span
        style={{
            ...guideStyles.badge,
            background: advisory ? ADVISORY_COLOUR : TIER_COLOURS[tier],
        }}
        data-tier={tier}
    >
        {advisory ? 'Worth a look' : TIER_LABELS[tier]}
    </span>
);

TierBadge.defaultProps = { advisory: false };
TierBadge.propTypes = { tier: string.isRequired, advisory: bool };

/*
 * Why this type of problem matters and what to do about it, in the
 * data team's words, shown whenever a type is selected.
 */
const ErrorGuide = ({ group }) => {
    const guide = codeGuide(group.code);
    if (!guide) return null;
    let tone = {};
    if (group.auto) tone = guideStyles.boxAuto;
    else if (group.kind === KIND.CORRECTION) tone = guideStyles.boxFix;
    const examples = group.examples.filter(e => e.original_value).slice(0, 2);
    const tier = tierOf(group);
    return (
        <div style={{ ...guideStyles.box, ...tone }} data-tour="guide">
            <div style={guideStyles.title}>
                <TierBadge
                    tier={tier}
                    advisory={group.severity === SEVERITY.ADVISORY}
                />
                <span>
                    {guide.title}: {guide.problem}
                </span>
            </div>
            <div>
                <div style={guideStyles.label}>Why it matters</div>
                <div>{guide.why}</div>
            </div>
            <div>
                <div style={guideStyles.label}>
                    {group.auto ? 'What was done' : 'How to fix it'}
                </div>
                <ul style={guideStyles.list}>
                    {guide.fix.map(line => (
                        <li key={line}>{line}</li>
                    ))}
                </ul>
            </div>
            {examples.length > 0 && (
                <div style={guideStyles.example}>
                    In your list:{' '}
                    {examples
                        .map(e => `row ${e.row_number}: "${e.original_value}"`)
                        .join(' · ')}
                </div>
            )}
        </div>
    );
};

ErrorGuide.propTypes = { group: object.isRequired };

/*
 * The group-level actions for the selected error type: act on the
 * pattern once, then look at the rows underneath only if needed.
 */
const GroupHeader = ({ group, canAct, busy, decideGroup }) => {
    const internal = group.severity === SEVERITY.INTERNAL_NOTE;
    const isIssue = group.kind === KIND.ISSUE;
    const isRemoval = group.kind === KIND.REMOVAL;
    // Rows the contributor decided one by one keep that decision; the
    // group buttons act on the others. Once every row has been decided
    // one by one there are no "others", so the buttons cover all rows
    // again (clearing the row-by-row marks first).
    const byRow = group.by_row || 0;
    const rest = group.count - byRow;
    const everyRow = rest === 0;
    const onGroup = decision => decideGroup(group.key, decision, everyRow);
    const partial = byRow > 0 && !everyRow;
    const scope = everyRow ? group.count : rest;
    const others = partial ? `the other ${rest}` : `all ${group.count}`;
    const otherRows = partial
        ? `the other ${plural(rest, 'row')}`
        : plural(group.count, 'row');
    // Nothing left for the button to do once every row in scope
    // already carries that decision.
    const allAccepted = group.accepted >= scope;
    const allRejected = group.rejected >= scope;
    const allRemoved = group.removed + group.accepted >= scope;
    return (
        <div style={chipStyles.header}>
            <Typography variant="subheading">
                {groupTitle(group)}: {plural(group.count, 'row')}
            </Typography>
            {!internal && <ErrorGuide group={group} />}
            {group.auto && (
                <div style={styles.muted}>
                    Will be applied automatically when you submit. Keep all
                    originals turns it off for every row of this type; use a
                    row&rsquo;s own buttons for one.
                </div>
            )}
            <div style={styles.decisionText}>{groupStatus(group)}</div>
            {canAct && !internal && (
                <div style={chipStyles.headerActions}>
                    {group.kind === KIND.CORRECTION && (
                        <>
                            <Button
                                size="small"
                                variant="outlined"
                                color="primary"
                                disabled={busy || allAccepted}
                                onClick={() => onGroup(DECISION.ACCEPTED)}
                            >
                                Accept {others}
                            </Button>
                            <Button
                                size="small"
                                variant="outlined"
                                disabled={busy || allRejected}
                                onClick={() => onGroup(DECISION.REJECTED)}
                            >
                                Keep {others} originals
                            </Button>
                        </>
                    )}
                    {(isRemoval || isIssue) && (
                        <>
                            <Button
                                size="small"
                                variant="outlined"
                                color={isRemoval ? 'primary' : 'secondary'}
                                disabled={busy || allRemoved}
                                onClick={() =>
                                    onGroup(
                                        isRemoval
                                            ? DECISION.ACCEPTED
                                            : DECISION.REMOVED,
                                    )
                                }
                            >
                                Remove {otherRows}
                            </Button>
                            <Button
                                size="small"
                                variant="outlined"
                                disabled={busy || allRejected}
                                onClick={() => onGroup(DECISION.REJECTED)}
                            >
                                {isRemoval
                                    ? `Keep ${otherRows}`
                                    : `Leave ${others} as uploaded`}
                            </Button>
                        </>
                    )}
                    {isIssue && (
                        <span style={styles.muted}>or fix each row below</span>
                    )}
                    {isIssue && group.severity === SEVERITY.MUST_FIX && (
                        <span style={styles.muted}>
                            Left as uploaded, a human moderator will remove
                            these rows.
                        </span>
                    )}
                </div>
            )}
        </div>
    );
};

GroupHeader.propTypes = {
    group: object.isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decideGroup: func.isRequired,
};

/*
 * The Needs-you tab's own actions: every suggested fix at once, or
 * everything left as uploaded. Flags have no value to accept, so Accept
 * all only covers the corrections; rows decided one by one are left
 * alone, as with any group action.
 */
const AllHeader = ({ groups, canAct, busy, decideGroup }) => {
    const corrections = groups.filter(g => g.kind === KIND.CORRECTION);
    const sumRest = list =>
        list.reduce((n, g) => n + g.count - (g.by_row || 0), 0);
    const sumAll = list => list.reduce((n, g) => n + g.count, 0);
    const fixes = sumRest(corrections);
    const everything = sumRest(groups);
    const byRow = groups.reduce((n, g) => n + (g.by_row || 0), 0);
    const flagged = groups.length - corrections.length;
    // Once every row was decided one by one the buttons cover all rows
    // again, clearing the row-by-row marks first.
    const everyRow = byRow > 0 && everything === 0;
    const partial = byRow > 0 && !everyRow;
    const fixCount = everyRow ? sumAll(corrections) : fixes;
    const keepCount = everyRow ? sumAll(groups) : everything;
    if (!canAct || !groups.length) return null;
    return (
        <div style={chipStyles.header}>
            <div style={chipStyles.headerActions}>
                <Button
                    size="small"
                    variant="outlined"
                    color="primary"
                    disabled={busy || !fixCount}
                    onClick={() =>
                        decideGroup(
                            corrections.map(g => g.key),
                            DECISION.ACCEPTED,
                            everyRow,
                        )
                    }
                >
                    Accept {partial ? 'the other' : 'all'}{' '}
                    {plural(fixCount, 'suggested fix', 'suggested fixes')}
                </Button>
                <Button
                    size="small"
                    variant="outlined"
                    disabled={busy || !keepCount}
                    onClick={() =>
                        decideGroup(
                            groups.map(g => g.key),
                            DECISION.REJECTED,
                            everyRow,
                        )
                    }
                >
                    Keep {partial ? 'the rest' : 'everything'} as uploaded
                </Button>
                <span style={styles.muted}>
                    {flagged > 0 &&
                        'Flagged rows have nothing to accept: fix or remove them by type or by row. '}
                    Or pick a type above.
                </span>
            </div>
        </div>
    );
};

AllHeader.propTypes = {
    groups: arrayOf(object).isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decideGroup: func.isRequired,
};

const AUTO = 'auto';

const chipProps = (key, active) => ({
    clickable: true,
    color: active === key ? 'primary' : 'default',
    variant: active === key ? 'default' : 'outlined',
    role: 'tab',
    'aria-selected': active === key,
});

/*
 * Actions on the rows the contributor ticked. They touch only the
 * suggestions shown on the current tab, go out as one request, and
 * count as row-by-row decisions so a later group action leaves them be.
 */
const BulkBar = ({ rows, selected, busy, decide, onClear }) => {
    const picked = rows.filter(r => selected.has(r.row_number));
    const suggestions = picked.reduce(
        (acc, r) =>
            acc.concat(
                r.suggestions.filter(
                    s => s.severity !== SEVERITY.INTERNAL_NOTE,
                ),
            ),
        [],
    );
    const fixes = suggestions.filter(s => s.kind === KIND.CORRECTION);
    if (!picked.length) return null;
    const send = (list, decision) => {
        decide(list.map(s => ({ id: s.id, decision })));
        onClear();
    };
    return (
        <div style={styles.bulkBar} data-tour="bulk">
            <span style={styles.bulkCount}>
                {plural(picked.length, 'row')} selected:
            </span>
            {fixes.length > 0 && (
                <Button
                    size="small"
                    variant="outlined"
                    color="primary"
                    disabled={busy}
                    onClick={() => send(fixes, DECISION.ACCEPTED)}
                >
                    Accept{' '}
                    {plural(fixes.length, 'suggested fix', 'suggested fixes')}
                </Button>
            )}
            <Button
                size="small"
                variant="outlined"
                disabled={busy}
                onClick={() => send(suggestions, DECISION.REJECTED)}
            >
                Keep as uploaded
            </Button>
            <Button
                size="small"
                variant="outlined"
                color="secondary"
                disabled={busy}
                onClick={() => send(suggestions, DECISION.REMOVED)}
            >
                Remove {plural(picked.length, 'row')}
            </Button>
            <Button size="small" disabled={busy} onClick={onClear}>
                Clear selection
            </Button>
        </div>
    );
};

BulkBar.propTypes = {
    rows: arrayOf(object).isRequired,
    selected: object.isRequired,
    busy: bool.isRequired,
    decide: func.isRequired,
    onClear: func.isRequired,
};

/*
 * The chips, in tiers: what needs the contributor, split into problems
 * that block approval and fixes that are recommended, one chip per
 * error type plus "Needs you". The automatic fixes open from the
 * tracker's "View fixes" into a row of their own, to inspect and turn
 * off by type. Lists run to thousands of rows; the errors do not come
 * in thousands of kinds.
 */
export const GroupTabs = ({
    groups,
    rows,
    canAct,
    busy,
    decide,
    decideGroup,
    showAuto,
    onShowAuto,
}) => {
    const [selected, setSelected] = useState(ALL);
    const [picked, setPicked] = useState(new Set());
    const attention = groups.filter(g => !g.auto);
    const automatic = groups.filter(g => g.auto);
    const blockers = attention.filter(g => tierOf(g) === TIER.BLOCKS);
    const recommended = attention.filter(g => tierOf(g) !== TIER.BLOCKS);
    const current = groups.find(g => g.key === selected);
    let active = ALL;
    if (current) {
        active = selected;
    } else if (selected === AUTO) {
        active = AUTO;
    }
    const autoRows = new Set(
        automatic.reduce((acc, g) => acc.concat(g.rows), []),
    ).size;
    const attentionRows = new Set(
        attention.reduce((acc, g) => acc.concat(g.rows), []),
    ).size;

    // Closing the automatic row while one of its chips is selected
    // drops back to Needs you.
    const onAutoTab = current && current.auto;
    useEffect(() => {
        if (!showAuto && (active === AUTO || onAutoTab)) setSelected(ALL);
    }, [showAuto, active, onAutoTab]);

    const filter = (() => {
        if (current) return s => suggestionKey(s) === current.key;
        if (active === AUTO) return isAuto;
        return s => !isAuto(s);
    })();

    const select = key => {
        setSelected(key);
        setPicked(new Set());
    };
    const shown = visibleRows(rows, filter);
    const toggle = rowNumber => {
        const next = new Set(picked);
        if (next.has(rowNumber)) next.delete(rowNumber);
        else next.add(rowNumber);
        setPicked(next);
    };
    const allPicked =
        shown.length > 0 && shown.every(r => picked.has(r.row_number));
    const chip = group => (
        <Chip
            key={group.key}
            label={chipLabel(group)}
            onClick={() => select(group.key)}
            {...chipProps(group.key, active)}
        />
    );

    return (
        <div>
            <div style={chipStyles.tiers} role="tablist" data-tour="chips">
                <div style={chipStyles.tier}>
                    <span style={chipStyles.tierLabel} />
                    <div style={chipStyles.tierChips}>
                        <Chip
                            label={`Needs you (${plural(
                                attentionRows,
                                'row',
                            )})`}
                            onClick={() => select(ALL)}
                            {...chipProps(ALL, active)}
                        />
                        {!attention.length && (
                            <span style={styles.muted}>
                                Nothing needs your decision.
                            </span>
                        )}
                    </div>
                </div>
                {blockers.length > 0 && (
                    <div style={chipStyles.tier}>
                        <span
                            style={{
                                ...chipStyles.tierLabel,
                                color: TIER_COLOURS[TIER.BLOCKS],
                            }}
                        >
                            {TIER_LABELS[TIER.BLOCKS]}
                        </span>
                        <div style={chipStyles.tierChips}>
                            {blockers.map(chip)}
                        </div>
                    </div>
                )}
                {recommended.length > 0 && (
                    <div style={chipStyles.tier}>
                        <span
                            style={{
                                ...chipStyles.tierLabel,
                                color: TIER_COLOURS[TIER.RECOMMENDED],
                            }}
                        >
                            {TIER_LABELS[TIER.RECOMMENDED]}
                        </span>
                        <div style={chipStyles.tierChips}>
                            {recommended.map(chip)}
                        </div>
                    </div>
                )}
                {showAuto && automatic.length > 0 && (
                    <div style={chipStyles.tier} data-tour="automatic-row">
                        <span style={chipStyles.tierLabel}>Automatic</span>
                        <div style={chipStyles.tierChips}>
                            <Chip
                                label={`All automatic (${plural(
                                    autoRows,
                                    'row',
                                )})`}
                                onClick={() => select(AUTO)}
                                {...chipProps(AUTO, active)}
                            />
                            {automatic.map(chip)}
                            {onShowAuto && (
                                <Button
                                    size="small"
                                    onClick={() => onShowAuto(false)}
                                >
                                    Hide
                                </Button>
                            )}
                        </div>
                    </div>
                )}
            </div>
            {current && (
                <GroupHeader
                    group={current}
                    canAct={canAct}
                    busy={busy}
                    decideGroup={decideGroup}
                />
            )}
            {active === ALL && (
                <AllHeader
                    groups={attention}
                    canAct={canAct}
                    busy={busy}
                    decideGroup={decideGroup}
                />
            )}
            {canAct && shown.length > 1 && (
                <label
                    style={styles.selectAll}
                    htmlFor="list-cleaning-select-all"
                >
                    <Checkbox
                        checked={allPicked}
                        indeterminate={!allPicked && picked.size > 0}
                        onChange={() =>
                            setPicked(
                                allPicked
                                    ? new Set()
                                    : new Set(shown.map(r => r.row_number)),
                            )
                        }
                        disabled={busy}
                        color="primary"
                        id="list-cleaning-select-all"
                        inputProps={{ 'aria-label': 'Select all rows shown' }}
                    />
                    Select all {plural(shown.length, 'row')} on this tab
                </label>
            )}
            {canAct && (
                <BulkBar
                    rows={shown}
                    selected={picked}
                    busy={busy}
                    decide={decide}
                    onClear={() => setPicked(new Set())}
                />
            )}
            <SuggestionRows
                rows={rows}
                canAct={canAct}
                busy={busy}
                decide={decide}
                filter={filter}
                selected={picked}
                onToggle={canAct ? toggle : null}
            />
        </div>
    );
};

GroupTabs.defaultProps = { showAuto: false, onShowAuto: null };
GroupTabs.propTypes = {
    groups: arrayOf(object).isRequired,
    rows: arrayOf(object).isRequired,
    canAct: bool.isRequired,
    busy: bool.isRequired,
    decide: func.isRequired,
    decideGroup: func.isRequired,
    showAuto: bool,
    onShowAuto: func,
};

export const DownloadFixedList = ({ listID, applied }) => (
    <Button
        size="small"
        variant="outlined"
        color="primary"
        href={makeFacilityListCleaningDownloadURL(listID)}
        download
        title={
            applied
                ? 'Download your list with the applied changes, removed rows last'
                : 'Apply your changes first; the download reflects the list as it stands'
        }
    >
        Download {applied ? 'fixed' : 'current'} list (CSV)
    </Button>
);

DownloadFixedList.propTypes = {
    listID: number.isRequired,
    applied: bool.isRequired,
};
