import COLOURS from '../../../util/COLOURS';

export const claimIntroStyles = theme => ({
    root: {
        background: theme.palette.background.grey,
        padding: '48px 5% 120px 5%',
        [theme.breakpoints.down('sm')]: {
            padding: '24px 5% 24px 5%',
        },
    },
    container: {},
    heroSection: {
        marginBottom: theme.spacing.unit * 3,
        marginTop: 0,
        paddingTop: 0,
    },
    title: {
        fontSize: '56px',
        fontWeight: 900,
        color: COLOURS.JET_BLACK,
        marginBottom: theme.spacing.unit,
        [theme.breakpoints.down('sm')]: {
            fontSize: '36px',
        },
    },
    subtitle: {
        fontSize: '18px',
        fontWeight: theme.typography.fontWeightSemiBold,
        margin: '24px 0 32px 0',
    },
    actionsInner: {
        display: 'flex',
        flexDirection: 'row',
        width: '100%',
        justifyContent: 'center',
        gap: '24px',
        padding: '48px 0',
        [theme.breakpoints.down('sm')]: {
            flexDirection: 'column',
            padding: '24px 0',
        },
    },
    backButton: {
        width: '200px',
        height: '49px',
        borderRadius: 0,
        textTransform: 'none',
        fontSize: '18px',
        fontWeight: theme.typography.fontWeightExtraBold,
        border: '1px solid #0D1128',
        [theme.breakpoints.down('sm')]: {
            width: '100%',
        },
    },
    continueButton: {
        width: '200px',
        height: '49px',
        borderRadius: 0,
        textTransform: 'none',
        backgroundColor: theme.palette.action.main,
        color: theme.palette.common.black,
        '&:hover': {
            backgroundColor: theme.palette.action.dark,
        },
        fontSize: '18px',
        fontWeight: theme.typography.fontWeightExtraBold,
        boxShadow: 'none',
        [theme.breakpoints.down('sm')]: {
            width: '100%',
        },
    },
});

export const claimInfoStyles = theme => ({
    root: {
        backgroundColor: COLOURS.WHITE,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        display: 'flex',
        flexDirection: 'column',
        padding: '40px 110px 0 110px',
        borderRadius: '0',
        [theme.breakpoints.down('sm')]: {
            padding: '24px 5% 0 5%',
        },
    },
    boxContainer: Object.freeze({
        padding: '20px 0 20px 0',
    }),
    boxHeader: {
        fontSize: '36px',
        fontWeight: 700,
        display: 'flex',
        alignItems: 'center',
    },
    stepNumber: {
        width: 36,
        height: 36,
        borderRadius: '50%',
        display: 'flex',
        lineHeight: '32px',
        justifyContent: 'center',
        fontWeight: theme.typography.fontWeightExtraBold,
        color: theme.palette.common.black,
        border: `2px solid ${theme.palette.common.black}`,
        boxShadow: '0 1px 2px rgba(0,0,0,0.08)',
        fontSize: '24px',
        marginRight: '10px',
    },
    boxList: {
        margin: 0,
        paddingLeft: '25px',
    },
    boxText: {
        fontSize: '18px',
        fontWeight: 600,
        lineHeight: '1.2',
    },
    boxDescription: {
        fontSize: '18px',
        fontWeight: 600,
        marginTop: '5px',
    },
    boxExamplesContainer: {
        display: 'flex',
        gap: theme.spacing.unit * 3,
        marginTop: '20px',
    },
    boxWarningContainer: {
        backgroundColor: COLOURS.LIGHT_RED,
        padding: theme.spacing.unit * 1.5,
        display: 'flex',
        alignItems: 'center',
        marginTop: '20px',
    },
    boxWarningText: {
        fontSize: '18px',
        display: 'flex',
        alignItems: 'center',
    },
    warningIcon: {
        color: COLOURS.MATERIAL_RED,
        marginRight: theme.spacing.unit,
        fontSize: 16,
        flexShrink: 0,
        marginTop: '2px',
    },

    // OLD STYLES
    stepBox: {
        padding: theme.spacing.unit * 2,
        marginBottom: 0,
        display: 'flex',
        flexDirection: 'column',
    },
    blueStep: {
        backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
        border: `1px solid ${COLOURS.LIGHT_BLUE_BORDER}`,
    },
    purpleStep: {
        backgroundColor: COLOURS.LIGHT_PURPLE_BG,
        border: `1px solid ${COLOURS.LIGHT_PURPLE_BORDER}`,
    },
    greenStep: {
        backgroundColor: COLOURS.LIGHT_GREEN,
        border: `1px solid ${COLOURS.LIGHT_GREEN_BORDER}`,
    },
    amberStep: {
        background: COLOURS.LIGHT_AMBER,
        border: `1px solid ${COLOURS.AMBER}`,
        boxShadow: '0 4px 12px rgba(255, 193, 7, 0.3)',
    },
    examplesContainer: {
        display: 'flex',
        gap: theme.spacing.unit * 3,
        marginTop: 'auto',
        paddingTop: theme.spacing.unit * 2,
        justifyContent: 'flex-start',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
    },
    exampleItem: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: 80,
        justifyContent: 'flex-start',
    },
    exampleImage: {
        width: 64,
        height: 64,
        objectFit: 'cover',
        borderRadius: theme.spacing.unit,
        cursor: 'pointer',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        transition: 'all 0.2s',
        '&:hover': {
            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
            transform: 'translateY(-2px)',
        },
    },
    separator: Object.freeze({
        margin: '1px 0',
        color: COLOURS.GREY,
    }),
});
