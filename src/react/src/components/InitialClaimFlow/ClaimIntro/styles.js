import COLOURS from '../../../util/COLOURS';

export const claimIntroStyles = theme => ({
    root: {
        backgroundColor: COLOURS.LIGHT_GREY,
        minHeight: 'calc(100vh - 64px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        paddingTop: theme.spacing.unit * 0,
        paddingBottom: theme.spacing.unit * 4,
    },
    container: {
        maxWidth: 1440,
        width: '100%',
        padding: theme.spacing.unit * 2,
        [theme.breakpoints.down('sm')]: {
            padding: theme.spacing.unit * 2,
        },
    },
    heroSection: {
        textAlign: 'center',
        marginBottom: theme.spacing.unit * 3,
        marginTop: 0,
        paddingTop: 0,
    },
    title: {
        fontSize: 48,
        fontWeight: 700,
        color: COLOURS.JET_BLACK,
        marginBottom: theme.spacing.unit,
        [theme.breakpoints.down('sm')]: {
            fontSize: 24,
        },
    },
    subtitle: {
        fontSize: 18,
        color: COLOURS.MEDIUM_GREY,
        maxWidth: 720,
        margin: '0 auto',
        lineHeight: 1.6,
    },
    actionsContainer: {
        backgroundColor: COLOURS.WHITE,
        padding: theme.spacing.unit * 2,
        marginTop: theme.spacing.unit * 3,
        marginBottom: 0,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    },
    actionsInner: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        [theme.breakpoints.down('sm')]: {
            flexDirection: 'column',
            gap: theme.spacing.unit * 2,
        },
    },
    backButton: {
        padding: '10px 24px',
        fontSize: 16,
        fontWeight: 800,
        borderColor: COLOURS.LIGHT_BORDER,
        textTransform: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        '&:hover': {
            backgroundColor: COLOURS.HOVER_GREY,
            borderColor: COLOURS.MEDIUM_BORDER,
        },
        [theme.breakpoints.down('sm')]: {
            width: '100%',
        },
    },
    continueButton: {
        padding: '10px 24px',
        fontSize: 18,
        fontWeight: 800,
        backgroundColor: theme.palette.action.main,
        color: COLOURS.BLACK,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        textTransform: 'none',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        '&:hover': {
            backgroundColor: theme.palette.action.dark,
            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
        },
        [theme.breakpoints.down('sm')]: {
            width: '100%',
        },
    },
    icon: {
        marginLeft: theme.spacing.unit,
        fontSize: 20,
        fontWeight: 800,
        display: 'flex',
        alignItems: 'center',
    },
});

export const claimInfoStyles = theme => ({
    root: {
        backgroundColor: COLOURS.WHITE,
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        padding: theme.spacing.unit * 3,
        '& > *:not(:last-child)': {
            marginBottom: theme.spacing.unit * 3,
        },
    },
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
