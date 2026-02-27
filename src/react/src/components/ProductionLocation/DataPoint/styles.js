import COLOURS from '../../../util/COLOURS';

/**
 * Data point styles matching design class:
 * "grid gap-6 py-3 group grid-cols-[140px_1fr]"
 * - grid, gap: 24px (gap-6), paddingY: 12px (py-3), columns: 140px 1fr
 * Plus matching font sizes, colors, and weights from the design.
 */
// eslint-disable-next-line no-unused-vars
export default theme =>
    Object.freeze({
        /* Root: grid container - same as design "grid gap-6 py-3 group grid-cols-[140px_1fr]" */
        root: Object.freeze({
            display: 'grid',
            gridTemplateColumns: '140px 1fr',
            gap: 24,
            paddingTop: 12,
            paddingBottom: 12,
            marginBottom: 24,
            '&:hover $tooltipIcon': Object.freeze({
                opacity: 1,
            }),
        }),
        /* First column: label */
        label: Object.freeze({
            fontSize: 14,
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
            fontWeight: 400,
        }),
        /* Second column: value + meta block */
        valueColumn: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: 4,
            minWidth: 0,
        }),
        valueRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: 8,
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
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
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
