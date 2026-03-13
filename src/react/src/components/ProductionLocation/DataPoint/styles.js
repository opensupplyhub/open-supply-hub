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
        metaRowWrapper: Object.freeze({
            marginLeft: '-16px',
        }),
        metaRowWrapperMultiline: Object.freeze({
            flexDirection: 'column',
        }),
        metaRow: Object.freeze({
            marginLeft: '16px',
            columnGap: '16px',
            alignItems: 'center',
        }),
        statusChip: Object.freeze({
            height: '24px',
            fontSize: '1rem',
            fontWeight: 600,
            borderRadius: 0,
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
        dateItem: Object.freeze({
            position: 'relative',
        }),
        metaDotSeparator: Object.freeze({
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
        sourcesButtonItem: Object.freeze({
            position: 'relative',
        }),
    });
