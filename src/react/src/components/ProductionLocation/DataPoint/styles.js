import COLOURS from '../../../util/COLOURS';

export default () =>
    Object.freeze({
        /* Root: Grid container - label column 140px, value column 1fr; spacing from Grid spacing={3} */
        root: Object.freeze({
            paddingTop: 12,
            paddingBottom: 12,
            marginBottom: 24,
            '&:hover $tooltipIcon': Object.freeze({
                opacity: 1,
            }),
        }),
        /* First column: label (140px) */
        labelColumn: Object.freeze({
            width: 140,
            flexShrink: 0,
        }),
        tooltipIconColumn: Object.freeze({
            width: 28,
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
        }),
        label: Object.freeze({
            fontSize: '16px',
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
        }),
        /* Second column: value + meta block */
        valueColumn: Object.freeze({
            minWidth: 0,
            flex: 1,
        }),
        valueWithTooltip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
        }),
        value: Object.freeze({
            fontSize: 16,
            lineHeight: 1.4,
            fontWeight: 700,
            color: COLOURS.NEAR_BLACK,
        }),
        tooltipIcon: Object.freeze({
            marginRight: 4,
            color: COLOURS.DARK_GREY,
            cursor: 'help',
            fontSize: 18,
            opacity: 0,
            transition: 'opacity 0.2s ease',
        }),
        statusChip: Object.freeze({
            height: 24,
            fontSize: 12,
            fontWeight: 600,
            borderRadius: 4,
            '& .MuiChip-label': Object.freeze({
                paddingLeft: 8,
                paddingRight: 8,
            }),
        }),
        claimedChip: Object.freeze({
            backgroundColor: COLOURS.DARK_GREEN,
            color: COLOURS.WHITE,
        }),
        crowdsourcedChip: Object.freeze({
            backgroundColor: COLOURS.DARK_SLATE_GREY,
            color: COLOURS.WHITE,
        }),
        metaRow: Object.freeze({
            fontSize: 14,
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
        }),
        metaRowSecondary: Object.freeze({
            fontSize: 14,
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
        }),
        contributor: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginRight: 12,
        }),
        personIcon: Object.freeze({
            marginRight: 4,
            fontSize: 18,
            color: COLOURS.DARK_GREY,
        }),
        dateBlock: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginRight: 4,
        }),
        dateIcon: Object.freeze({
            marginRight: 4,
            fontSize: 18,
            color: COLOURS.DARK_GREY,
        }),
        metaSeparator: Object.freeze({
            marginLeft: 4,
            marginRight: 4,
            color: COLOURS.DARK_GREY,
        }),
        sourcesButton: Object.freeze({
            textTransform: 'none',
            fontWeight: 500,
            fontSize: 14,
            padding: 0,
            minHeight: 0,
            textDecoration: 'underline',
            color: COLOURS.PURPLE,
            '&:hover': Object.freeze({
                backgroundColor: 'transparent',
                textDecoration: 'underline',
                color: COLOURS.DARK_PURPLE,
            }),
        }),
    });
