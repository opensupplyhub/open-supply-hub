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
        padding: '0 110px 0 110px',
        borderRadius: '0',
        [theme.breakpoints.down('sm')]: {
            padding: '24px 5% 0 5%',
        },
    },
    boxContainer: Object.freeze({
        padding: '40px 0 0 0',
    }),
    boxHeader: {
        fontSize: '36px',
        fontWeight: 700,
    },
    boxList: {
        margin: 0,
        marginTop: '20px',
        paddingLeft: '25px',
    },
    boxText: {
        fontSize: '18px',
        fontWeight: 600,
    },
    boxDescription: {
        fontSize: '18px',
        fontWeight: 600,
        marginTop: '20px',
    },
    boxExamplesContainer: {
        display: 'flex',
        gap: theme.spacing.unit * 3,
        marginTop: '20px',
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
    stepNumber: {
        width: 32,
        height: 32,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: COLOURS.WHITE,
        fontWeight: 600,
        fontSize: 18,
        marginRight: theme.spacing.unit * 1.5,
        flexShrink: 0,
    },
    blueNumber: {
        backgroundColor: COLOURS.MATERIAL_BLUE,
    },
    purpleNumber: {
        backgroundColor: COLOURS.MATERIAL_PURPLE,
    },
    greenNumber: {
        backgroundColor: COLOURS.MATERIAL_GREEN,
    },
    amberNumber: {
        background: COLOURS.ORANGE,
        boxShadow: '0 2px 8px rgba(245, 124, 0, 0.4)',
    },
    stepHeader: {
        display: 'flex',
        alignItems: 'flex-start',
        marginBottom: theme.spacing.unit * 1.5,
    },
    stepTitle: {
        fontSize: 24,
        fontWeight: 600,
        marginBottom: theme.spacing.unit * 0.5,
    },
    stepText: {
        fontSize: 18,
        lineHeight: 1.6,
    },
    bulletPoint: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: theme.spacing.unit,
    },
    bullet: {
        width: 6,
        height: 6,
        borderRadius: '50%',
        marginRight: theme.spacing.unit,
        flexShrink: 0,
    },
    blueBullet: {
        backgroundColor: COLOURS.MATERIAL_BLUE,
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
    purpleBorder: {
        border: `2px solid ${COLOURS.LIGHT_PURPLE_BORDER}`,
    },
    greenBorder: {
        border: `2px solid ${COLOURS.LIGHT_GREEN_BORDER}`,
    },
    exampleLabel: {
        fontSize: 14,
        textAlign: 'center',
        marginTop: theme.spacing.unit,
        fontWeight: 700,
        lineHeight: 1.2,
    },
    purpleLabel: {
        color: COLOURS.PURPLE_TEXT,
    },
    greenLabel: {
        color: COLOURS.GREEN_TEXT,
    },
    noteBox: {
        backgroundColor: COLOURS.NOTE_GREEN,
        padding: theme.spacing.unit * 1.5,
        marginTop: theme.spacing.unit,
    },
    maxValueBadge: {
        display: 'inline-flex',
        alignItems: 'center',
        backgroundColor: COLOURS.ORANGE,
        color: COLOURS.WHITE,
        padding: '6px 12px',
        borderRadius: 20,
        fontSize: 18,
        fontWeight: 700,
        marginBottom: theme.spacing.unit * 1.5,
        boxShadow: '0 2px 6px rgba(255, 160, 0, 0.4)',
    },
    warningBox: {
        backgroundColor: COLOURS.LIGHT_GREY,
        padding: theme.spacing.unit * 1.5,
        display: 'flex',
        alignItems: 'center',
    },
    warningIcon: {
        color: COLOURS.MATERIAL_RED,
        marginRight: theme.spacing.unit,
        fontSize: 16,
        flexShrink: 0,
    },
    link: {
        color: COLOURS.MATERIAL_BLUE,
        textDecoration: 'none',
        fontWeight: 500,
        '&:hover': {
            textDecoration: 'underline',
        },
    },
    dialogImage: {
        width: '100%',
        height: 'auto',
        maxHeight: '80vh',
        objectFit: 'contain',
    },
    closeButton: {
        position: 'absolute',
        right: theme.spacing.unit,
        top: theme.spacing.unit,
        color: theme.palette.grey[500],
    },
    twoColumnGrid: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        columnGap: theme.spacing.unit * 3,
        rowGap: theme.spacing.unit * 2,
        [theme.breakpoints.down('sm')]: {
            gridTemplateColumns: '1fr',
        },
    },
});
