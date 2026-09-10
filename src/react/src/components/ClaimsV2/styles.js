import COLOURS from '../../util/COLOURS';

/*
 * Skeleton styles for the claims dashboard v2 shell (OSDEV-3355).
 * Plain frozen style objects, matching Dashboard.jsx's approach; the
 * full visual treatment lands with the Queue view (OSDEV-3356) —
 * visual spec: https://claims-moderation-prototype.vercel.app
 */

export default Object.freeze({
    shell: Object.freeze({
        display: 'flex',
        alignItems: 'flex-start',
        gap: '16px',
        padding: '16px',
        fontSize: '14px',
    }),
    rail: Object.freeze({
        width: '300px',
        flex: 'none',
    }),
    railCard: Object.freeze({
        display: 'block',
        width: '100%',
        textAlign: 'left',
        padding: '8px 10px',
        marginBottom: '6px',
        border: `1px solid ${COLOURS.GREY}`,
        borderRadius: '6px',
        background: COLOURS.WHITE,
        cursor: 'pointer',
    }),
    railCardSelected: Object.freeze({
        borderColor: COLOURS.NAVY_BLUE,
    }),
    railCardMeta: Object.freeze({
        color: COLOURS.DARK_GREY,
        fontSize: '12px',
    }),
    workspace: Object.freeze({
        flex: 1,
        minWidth: 0,
    }),
    stageBox: Object.freeze({
        padding: '8px 12px',
        margin: '8px 0',
        border: `1px solid ${COLOURS.GREY}`,
        borderRadius: '6px',
        background: COLOURS.LIGHT_GREY,
    }),
    noteItem: Object.freeze({
        padding: '8px 0',
        borderTop: `1px solid ${COLOURS.GREY}`,
    }),
    noteTag: Object.freeze({
        display: 'inline-block',
        marginLeft: '6px',
        padding: '0 6px',
        borderRadius: '4px',
        fontSize: '11px',
        fontWeight: 700,
        background: COLOURS.LIGHT_GREY,
    }),
    noteMeta: Object.freeze({
        color: COLOURS.DARK_GREY,
        fontSize: '12px',
    }),
    railSearch: Object.freeze({
        width: '100%',
        padding: '6px 8px',
        marginBottom: '6px',
        border: `1px solid ${COLOURS.GREY}`,
        borderRadius: '6px',
        fontSize: '13px',
    }),
    railControls: Object.freeze({
        display: 'flex',
        gap: '6px',
        marginBottom: '8px',
    }),
    railSelect: Object.freeze({
        flex: 1,
        minWidth: 0,
        padding: '4px',
        border: `1px solid ${COLOURS.GREY}`,
        borderRadius: '6px',
        background: COLOURS.WHITE,
        fontSize: '12px',
    }),
    railSortButton: Object.freeze({
        flex: 'none',
        padding: '4px 8px',
        border: `1px solid ${COLOURS.GREY}`,
        borderRadius: '6px',
        background: COLOURS.WHITE,
        cursor: 'pointer',
        fontSize: '12px',
    }),
    stageHead: Object.freeze({
        display: 'flex',
        justifyContent: 'space-between',
        width: '100%',
        padding: '6px 8px',
        margin: '10px 0 6px',
        border: 'none',
        borderRadius: '4px',
        background: COLOURS.LIGHT_GREY,
        cursor: 'pointer',
        fontWeight: 700,
        fontSize: '12px',
        textAlign: 'left',
    }),
    stageAccentNew: Object.freeze({
        borderLeft: `4px solid ${COLOURS.NAVY_BLUE}`,
    }),
    stageAccentAwaiting: Object.freeze({
        borderLeft: `4px solid ${COLOURS.DARK_GREY}`,
    }),
    stageAccentOverdue: Object.freeze({
        borderLeft: `4px solid ${COLOURS.RED}`,
    }),
    stageCount: Object.freeze({
        color: COLOURS.DARK_GREY,
        fontWeight: 400,
    }),
    stageEmpty: Object.freeze({
        color: COLOURS.DARK_GREY,
        fontSize: '12px',
        padding: '2px 8px 6px',
    }),
    waitingBadge: Object.freeze({
        display: 'inline-block',
        marginLeft: '6px',
        padding: '0 5px',
        borderRadius: '4px',
        fontSize: '11px',
        fontWeight: 700,
        background: COLOURS.LIGHT_GREY,
    }),
    kbdHint: Object.freeze({
        marginTop: '10px',
        color: COLOURS.DARK_GREY,
        fontSize: '11.5px',
    }),
});
