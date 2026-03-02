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
            width: '165px',
            flexDirection: 'row',
        }),
        labelItem: Object.freeze({
            width: '80%',
        }),
        label: Object.freeze({
            fontSize: '16px',
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
        }),
        tooltipIconItem: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'center',
            width: '20%',
        }),
        /* Second column: value + meta block */
        valueColumn: Object.freeze({
            minWidth: 0,
            flex: 1,
        }),
        valueWithTooltip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginBottom: '4px',
        }),
        value: Object.freeze({
            fontSize: 16,
            lineHeight: 1.4,
            fontWeight: 500,
        }),
        tooltipIcon: Object.freeze({
            color: COLOURS.DARK_GREY,
            cursor: 'help',
            fontSize: 18,
            opacity: 0,
            transition: 'opacity 0.2s ease',
        }),
        statusChip: Object.freeze({
            height: 24,
            fontSize: '14px',
            fontWeight: 600,
            borderRadius: 0,
            '& .MuiChip-label': Object.freeze({
                paddingLeft: 8,
                paddingRight: 8,
            }),
        }),
        claimedChip: Object.freeze({
            backgroundColor: '#f0fdf480',
            color: COLOURS.DARK_GREEN,
        }),
        crowdsourcedChip: Object.freeze({
            backgroundColor: '#fff7ed80',
            color: '#C2410C',
        }),
        metaRow: Object.freeze({
            fontSize: 14,
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
            marginBottom: '4px',
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
        contributorName: Object.freeze({
            fontSize: '16px',
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
        dateText: Object.freeze({
            fontSize: '16px',
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
            fontSize: '16px',
            padding: 0,
            minHeight: 0,
            color: COLOURS.PURPLE,
            '&:hover': Object.freeze({
                backgroundColor: 'transparent',
                textDecoration: 'underline',
            }),
        }),
    });
