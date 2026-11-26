import COLOURS from '../../util/COLOURS';

const BORDER = `1px solid ${COLOURS.GREY}`;

/*
 * Styles for the organization level. Plain frozen style objects,
 * matching the approach of the claims dashboard v2 and Dashboard.jsx.
 */
export default Object.freeze({
    // AppGrid lays its children out in a wrapping flex row, so each
    // organization screen is one full-width block inside it.
    root: Object.freeze({
        width: '100%',
    }),
    section: Object.freeze({
        margin: '0 0 32px',
    }),
    sectionTitle: Object.freeze({
        fontSize: '20px',
        fontWeight: 700,
        margin: '0 0 4px',
    }),
    sectionHint: Object.freeze({
        fontSize: '14px',
        color: COLOURS.DARK_GREY,
        margin: '0 0 12px',
    }),
    headerRow: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        margin: '0 0 24px',
    }),
    organizationName: Object.freeze({
        fontSize: '28px',
        fontWeight: 700,
        margin: 0,
    }),
    meta: Object.freeze({
        fontSize: '14px',
        color: COLOURS.DARK_GREY,
        margin: '4px 0 0',
    }),
    chip: Object.freeze({
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: '12px',
        fontSize: '13px',
        fontWeight: 700,
        background: COLOURS.EXTRA_LIGHT_BLUE,
        color: COLOURS.DARK_BLUE,
    }),
    chipClaimed: Object.freeze({
        display: 'inline-block',
        padding: '2px 10px',
        borderRadius: '12px',
        fontSize: '13px',
        fontWeight: 700,
        background: COLOURS.LIGHT_GREEN,
        color: COLOURS.GREEN_TEXT,
        whiteSpace: 'nowrap',
    }),
    noWrap: Object.freeze({
        whiteSpace: 'nowrap',
    }),
    card: Object.freeze({
        border: BORDER,
        borderRadius: '8px',
        padding: '16px',
        background: COLOURS.WHITE,
    }),
    invitationCard: Object.freeze({
        border: `1px solid ${COLOURS.LIGHT_BLUE_BORDER}`,
        borderRadius: '8px',
        padding: '16px',
        margin: '0 0 12px',
        background: COLOURS.EXTRA_LIGHT_BLUE,
    }),
    emptyState: Object.freeze({
        border: BORDER,
        borderRadius: '8px',
        padding: '24px',
        fontSize: '16px',
        lineHeight: 1.5,
    }),
    error: Object.freeze({
        color: COLOURS.MATERIAL_RED,
        fontSize: '14px',
        margin: '8px 0',
    }),
    actionsRow: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '8px',
        margin: '12px 0 0',
    }),
    inviteForm: Object.freeze({
        display: 'flex',
        alignItems: 'flex-end',
        flexWrap: 'wrap',
        gap: '16px',
        margin: '0 0 16px',
    }),
    inviteEmailField: Object.freeze({
        minWidth: '280px',
    }),
    tableWrapper: Object.freeze({
        border: BORDER,
        borderRadius: '8px',
        overflowX: 'auto',
    }),
    pager: Object.freeze({
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        gap: '12px',
        margin: '8px 0 0',
        fontSize: '14px',
    }),
    subTabs: Object.freeze({
        display: 'flex',
        gap: '8px',
        margin: '0 0 12px',
    }),
    filters: Object.freeze({
        display: 'flex',
        alignItems: 'flex-end',
        flexWrap: 'wrap',
        gap: '16px',
        margin: '0 0 24px',
    }),
    filterField: Object.freeze({
        minWidth: '180px',
    }),
    tiles: Object.freeze({
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
        gap: '16px',
        margin: '0 0 24px',
    }),
    tileValue: Object.freeze({
        fontSize: '32px',
        fontWeight: 700,
        lineHeight: 1.1,
    }),
    tileLabel: Object.freeze({
        fontSize: '14px',
        color: COLOURS.DARK_GREY,
        margin: '4px 0 0',
    }),
    charts: Object.freeze({
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '16px',
        margin: '0 0 32px',
    }),
    chartTitle: Object.freeze({
        fontSize: '16px',
        fontWeight: 700,
        margin: '0 0 12px',
    }),
    barRow: Object.freeze({
        display: 'grid',
        gridTemplateColumns: '140px 1fr 48px',
        alignItems: 'center',
        gap: '8px',
        margin: '0 0 6px',
        fontSize: '14px',
    }),
    barLabel: Object.freeze({
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
    }),
    barTrack: Object.freeze({
        height: '14px',
        borderRadius: '4px',
        background: COLOURS.LIGHT_GREY,
    }),
    barFill: Object.freeze({
        height: '14px',
        borderRadius: '4px',
        background: COLOURS.NAVY_BLUE,
    }),
    barValue: Object.freeze({
        textAlign: 'right',
        fontVariantNumeric: 'tabular-nums',
    }),
    checklist: Object.freeze({
        listStyle: 'none',
        margin: 0,
        padding: 0,
        border: BORDER,
        borderRadius: '8px',
    }),
    checklistItem: Object.freeze({
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
        padding: '12px 16px',
        borderBottom: `1px solid ${COLOURS.LIGHT_GREY}`,
    }),
    checklistTitle: Object.freeze({
        fontSize: '16px',
        fontWeight: 700,
    }),
    checkDone: Object.freeze({
        flex: '0 0 22px',
        height: '22px',
        borderRadius: '50%',
        background: COLOURS.LIGHT_GREEN,
        color: COLOURS.GREEN_TEXT,
        fontWeight: 700,
        textAlign: 'center',
        lineHeight: '22px',
    }),
    checkTodo: Object.freeze({
        flex: '0 0 20px',
        height: '20px',
        borderRadius: '50%',
        border: `1px solid ${COLOURS.DARK_GREY}`,
    }),
    plainList: Object.freeze({
        listStyle: 'none',
        margin: '0 0 8px',
        padding: 0,
    }),
    plainListItem: Object.freeze({
        padding: '6px 0',
        borderBottom: `1px solid ${COLOURS.LIGHT_GREY}`,
        fontSize: '15px',
    }),
    detailRow: Object.freeze({
        display: 'grid',
        gridTemplateColumns: '220px 1fr',
        gap: '12px',
        padding: '6px 0',
        borderBottom: `1px solid ${COLOURS.LIGHT_GREY}`,
        fontSize: '14px',
    }),
    detailLabel: Object.freeze({
        color: COLOURS.DARK_GREY,
    }),
    detailHeading: Object.freeze({
        fontSize: '16px',
        fontWeight: 700,
        margin: '20px 0 8px',
    }),
});
