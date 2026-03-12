import COLOURS from '../../../util/COLOURS';

export default () =>
    Object.freeze({
        root: Object.freeze({
            paddingTop: '12px',
            paddingBottom: '12px',
            flexWrap: 'nowrap',
            '&:hover $tooltipIcon': Object.freeze({
                opacity: 1,
                '& > svg': Object.freeze({
                    '&:hover': Object.freeze({
                        color: COLOURS.PURPLE,
                    }),
                }),
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
            fontSize: '1.125rem',
            lineHeight: 1.7,
            color: COLOURS.DARK_GREY,
            wordWrap: 'break-word',
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
            flexDirection: 'column',
        }),
        valueWithTooltip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginBottom: '4px',
        }),
        value: Object.freeze({
            fontSize: '1.125rem',
            fontWeight: 600,
            lineHeight: 1.4,
        }),
        statusChip: Object.freeze({
            height: '24px',
            fontSize: '1rem',
            fontWeight: 600,
            borderRadius: 0,
            marginRight: '8px',
            '& .MuiChip-label': Object.freeze({
                paddingLeft: '8px',
                paddingRight: '8px',
            }),
        }),
        claimedChip: Object.freeze({
            backgroundColor: COLOURS.CLAIMED_CHIP_BG,
            color: COLOURS.DARK_GREEN,
        }),
        crowdsourcedChip: Object.freeze({
            backgroundColor: COLOURS.CROWDSOURCED_CHIP_BG,
            color: COLOURS.CROWDSOURCED_CHIP_TEXT,
        }),
        metaRowContainer: Object.freeze({
            marginLeft: '-16px',
        }),
        metaRow: Object.freeze({
            fontSize: '1rem',
            width: 'fit-content',
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
            marginLeft: '16px',
            alignItems: 'center',
            flexWrap: 'wrap',
        }),
        metaRowSecondary: Object.freeze({
            fontSize: '1rem',
            lineHeight: 1.43,
            color: COLOURS.DARK_GREY,
            width: 'fit-content',
            alignItems: 'center',
            flexWrap: 'wrap',
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
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
        }),
        contributorName: Object.freeze({
            fontSize: '1.125rem',
            lineHeight: 1.7,
            color: COLOURS.DARK_GREY,
        }),
        contributorNameLink: Object.freeze({
            textDecoration: 'none',
            cursor: 'pointer',
            fontWeight: 500,
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        dateItem: Object.freeze({
            position: 'relative',
            marginLeft: '16px',
            '&::before': Object.freeze({
                content: "'·'",
                fontSize: '1.25rem',
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
            marginRight: '4px',
            fontSize: '0.8125rem',
            color: COLOURS.DARK_GREY,
            marginTop: '3px',
        }),
        dateText: Object.freeze({
            fontSize: '1.125rem',
            lineHeight: 1.7,
            color: COLOURS.DARK_GREY,
        }),
        metaSeparator: Object.freeze({
            marginLeft: '4px',
            marginRight: '4px',
            color: COLOURS.DARK_GREY,
        }),
        sourcesButtonItem: Object.freeze({
            marginLeft: '16px',
            position: 'relative',
            '&::before': Object.freeze({
                content: "'·'",
                fontSize: '1.25rem',
                position: 'absolute',
                left: '-9px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: COLOURS.DARK_GREY,
            }),
        }),
    });
