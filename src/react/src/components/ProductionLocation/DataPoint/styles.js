import COLOURS from '../../../util/COLOURS';

export default () =>
    Object.freeze({
        root: Object.freeze({
            paddingTop: 12,
            paddingBottom: 12,
            '&:hover $tooltipIcon': Object.freeze({
                opacity: 1,
            }),
        }),
        labelColumn: Object.freeze({
            width: '165px',
            flexDirection: 'row',
        }),
        labelItem: Object.freeze({
            width: '80%',
        }),
        label: Object.freeze({
            fontSize: '18px',
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
        }),
        tooltipIconItem: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            width: '20%',
        }),
        tooltipIcon: Object.freeze({
            opacity: 0,
        }),
        valueColumn: Object.freeze({
            minWidth: 0,
            flex: 1,
            overflow: 'hidden',
        }),
        valueWithTooltip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginBottom: '4px',
        }),
        value: Object.freeze({
            fontSize: '18px',
            fontWeight: 600,
            lineHeight: 1.4,
        }),
        statusChip: Object.freeze({
            height: 24,
            fontSize: '16px',
            fontWeight: 600,
            borderRadius: 0,
            marginRight: '8px',
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
        metaRowContainer: Object.freeze({
            marginLeft: '-16px',
        }),
        metaRow: Object.freeze({
            fontSize: '16px',
            width: 'fit-content',
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
            marginBottom: '4px',
            marginLeft: '16px',
        }),
        metaRowSecondary: Object.freeze({
            fontSize: '16px',
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
            width: 'fit-content',
        }),
        contributorItem: Object.freeze({
            width: 'fit-content',
        }),
        contributor: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
        }),
        personIcon: Object.freeze({
            marginRight: '4px',
            marginTop: '2px',
            fontSize: '16px',
            color: COLOURS.DARK_GREY,
        }),
        contributorName: Object.freeze({
            fontSize: '18px',
            color: COLOURS.DARK_GREY,
        }),
        dateItem: Object.freeze({
            position: 'relative',
            marginLeft: '16px',
            '&::before': Object.freeze({
                content: "'·'",
                fontSize: '20px',
                position: 'absolute',
                left: '-9px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: COLOURS.DARK_GREY,
            }),
        }),
        dateBlock: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
        }),
        dateIcon: Object.freeze({
            marginRight: 4,
            fontSize: '13px',
            color: COLOURS.DARK_GREY,
            marginTop: '3px',
        }),
        dateText: Object.freeze({
            fontSize: '18px',
            color: COLOURS.DARK_GREY,
        }),
        metaSeparator: Object.freeze({
            marginLeft: 4,
            marginRight: 4,
            color: COLOURS.DARK_GREY,
        }),
        sourcesButtonItem: Object.freeze({
            marginLeft: '16px',
            position: 'relative',
            '&::before': Object.freeze({
                content: "'·'",
                fontSize: '20px',
                position: 'absolute',
                left: '-9px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: COLOURS.DARK_GREY,
            }),
        }),
        sourcesButton: Object.freeze({
            textTransform: 'none',
            fontWeight: 600,
            fontSize: '18px',
            padding: 0,
            minHeight: 0,
            color: COLOURS.PURPLE,
            '&:hover': Object.freeze({
                backgroundColor: 'transparent',
                textDecoration: 'underline',
            }),
        }),
    });
