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
        textAlign: 'center',
    },
    subtitle: {
        fontSize: '18px',
        fontWeight: theme.typography.fontWeightSemiBold,
        margin: '24px 0 32px 0',
        textAlign: 'center',
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
            gap: '12px',
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
    boxContainerWrapper: {
        display: 'flex',
        maxWidth: '1071px',
        marginBottom: '10px',
        margin: '0 auto',
        width: '100%',
    },
    boxContainerWrapperColumn: {
        [theme.breakpoints.down('sm')]: {
            flexDirection: 'column',
        },
    },
    boxContainer: {
        padding: '20px',
        border: '1px solid #E0E0E0',
        width: '100%',
    },
    boxContainerHalf: {
        display: 'flex',
        flex: 1,
        marginRight: '10px',
        '&:last-child': {
            marginRight: 0,
        },
        [theme.breakpoints.down('sm')]: {
            marginRight: '0',
        },
    },
    boxHeader: {
        fontSize: '36px',
        fontWeight: 700,
        display: 'inline-flex',
        alignItems: 'center',
        marginBottom: theme.spacing.unit * 2,
    },
    stepTitle: {
        lineHeight: '1.2',
        fontSize: '26px',
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
        marginTop: '4px',
        flexShrink: 0,
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
        color: COLOURS.DARK_GREY,
    },
    boxDescriptionMargin: {
        marginBottom: '15px',
    },
    boxExamplesContainer: {
        display: 'flex',
        gap: theme.spacing.unit * 3,
        marginTop: '20px',
    },
    boxWarningContainer: {
        maxWidth: '1071px',
        boxSizing: 'border-box',
        backgroundColor: COLOURS.LIGHT_RED,
        padding: theme.spacing.unit * 1.5,
        display: 'flex',
        alignItems: 'center',
    },
    boxWarningText: {
        fontSize: '18px',
        display: 'inline-flex',
        alignItems: 'center',
    },
    warningIcon: {
        color: COLOURS.MATERIAL_RED,
        marginRight: theme.spacing.unit,
        fontSize: 16,
        marginTop: '2px',
    },
    boxWarningTextIcon: {
        display: 'inline-flex',
        alignItems: 'center',
        marginRight: theme.spacing.unit,
    },
    blueStep: {
        backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
        border: `1px solid ${theme.palette.common.black}`,
        color: theme.palette.common.black,
    },
    purpleStep: {
        backgroundColor: COLOURS.LIGHT_PURPLE,
        border: `1px solid ${theme.palette.common.black}`,
        color: theme.palette.common.black,
    },
    greenStep: {
        backgroundColor: COLOURS.LIGHT_GREEN,
        border: `1px solid ${theme.palette.common.black}`,
        color: theme.palette.common.black,
    },
    amberStep: {
        background: COLOURS.LIGHT_AMBER,
        border: `1px solid ${theme.palette.common.black}`,
        color: theme.palette.common.black,
    },
    defaultLabel: {
        fontWeight: theme.typography.fontWeightSemiBold,
        textAlign: 'center',
        color: COLOURS.DARK_GREY,
    },
    noBorder: {
        border: 'none',
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
    maxValueBadge: {
        cursor: 'help',
        marginLeft: 10,
        width: 24,
        height: 24,
        padding: 0,
        borderRadius: '50%',
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: 14,
        fontWeight: theme.typography.fontWeightBold,
        backgroundColor: theme.palette.action.main,
        color: theme.palette.common.black,
        flexShrink: 0,
    },
});
