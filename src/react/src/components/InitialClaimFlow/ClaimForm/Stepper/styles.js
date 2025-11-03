import COLOURS from '../../../../util/COLOURS';

const stepperStyles = () => ({
    stepperRoot: Object.freeze({
        backgroundColor: 'transparent',
        padding: 0,
        display: 'flex',
        justifyContent: 'flex-start',
    }),
    stepIconContainer: Object.freeze({
        '& > svg': {
            fontSize: '40px',
        },
    }),
    stepIconContainerClickable: Object.freeze({
        cursor: 'pointer',
        pointerEvents: 'auto',
    }),
    stepRoot: Object.freeze({
        '&:last-child': {
            paddingRight: '8px',
        },
        '&:first-child': {
            paddingLeft: '8px',
        },
    }),
    stepLabelRoot: Object.freeze({
        pointerEvents: 'none',
        cursor: 'default !important',
    }),
    stepLabelContainer: Object.freeze({
        '& > span': {
            marginTop: '4px !important',
        },
    }),
    stepContent: Object.freeze({
        flexDirection: 'column',
        alignItems: 'center',
    }),
    stepLabel: Object.freeze({
        fontSize: '17px',
        fontWeight: 600,
        lineHeight: '1.5',
    }),
    stepSubtitle: Object.freeze({
        fontSize: '16px',
        color: COLOURS.DARK_GREY,
        fontWeight: 500,
        lineHeight: '1.2',
    }),
    stepTime: Object.freeze({
        alignItems: 'center',
        justifyContent: 'center',
    }),
    stepTimeIconContainer: Object.freeze({
        height: 'fit-content',
        width: 'fit-content',
        marginRight: '4px',
        marginTop: '2px',
    }),
    stepTimeIcon: Object.freeze({
        fontSize: '15px',
        color: COLOURS.DARK_GREY,
    }),
    stepTimeIconActive: Object.freeze({
        color: COLOURS.PURPLE,
    }),
    stepTimeText: Object.freeze({
        fontSize: '15px',
        fontWeight: 500,
        color: COLOURS.DARK_GREY,
    }),
    stepTimeTextActive: Object.freeze({
        color: COLOURS.PURPLE,
    }),
    connectorRoot: Object.freeze({
        top: '20px',
        left: 'calc(50% + 36px)',
        right: 'calc(-50% + 36px)',
    }),
    connectorLine: Object.freeze({
        borderColor: COLOURS.GREY,
        borderTopWidth: 2,
    }),
});

export default stepperStyles;
