import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        container: Object.freeze({
            borderTop: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            marginTop: '12px',
            paddingTop: '4px',
        }),
        header: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            padding: '4px 0',
            userSelect: 'none',
        }),
        toggleLabel: Object.freeze({
            fontSize: '0.875rem',
            fontWeight: 600,
            color: COLOURS.DARK_GREY,
        }),
        chevron: Object.freeze({
            color: COLOURS.DARK_GREY,
        }),
        contentArea: Object.freeze({
            paddingBottom: '8px',
        }),
        provenanceRow: Object.freeze({
            fontSize: '0.875rem',
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        provenanceLabel: Object.freeze({
            fontWeight: 600,
            marginRight: '4px',
        }),
        provenanceLink: Object.freeze({
            color: COLOURS.PURPLE,
            wordBreak: 'break-all',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
    });
