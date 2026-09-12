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
});
