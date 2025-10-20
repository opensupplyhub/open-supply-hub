import COLOURS from '../../../util/COLOURS';

const stepperStyles = theme => ({
    stepperRoot: Object.freeze({
        backgroundColor: 'transparent',
        paddingTop: theme.spacing.unit * 3,
        paddingBottom: theme.spacing.unit * 3,
    }),
    step: Object.freeze({
        cursor: 'pointer',
        '& .MuiStepIcon-root': {
            width: 40,
            height: 40,
            border: `2px solid ${COLOURS.GREY}`,
            borderRadius: '50%',
            backgroundColor: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.3s',
        },
        '& .MuiStepIcon-active': {
            border: `2px solid ${theme.palette.primary.main}`,
            backgroundColor: theme.palette.primary.main,
            color: '#fff',
        },
        '& .MuiStepIcon-completed': {
            border: `2px solid ${theme.palette.primary.main}`,
            backgroundColor: theme.palette.primary.main,
            color: '#fff',
        },
    }),
    stepLabel: Object.freeze({
        cursor: 'pointer',
        '& .MuiStepLabel-label': {
            fontSize: '0.875rem',
            fontWeight: 500,
            marginTop: theme.spacing.unit,
        },
    }),
    stepLabelActive: Object.freeze({
        '& .MuiStepLabel-label': {
            fontWeight: 600,
            color: theme.palette.text.primary,
        },
    }),
    stepLabelCompleted: Object.freeze({
        '& .MuiStepLabel-label': {
            color: theme.palette.text.primary,
        },
    }),
    stepIcon: Object.freeze({
        width: 40,
        height: 40,
        fontSize: '1.25rem',
    }),
    stepIconActive: Object.freeze({
        color: '#fff',
        backgroundColor: theme.palette.primary.main,
        border: `2px solid ${theme.palette.primary.main}`,
    }),
    stepIconCompleted: Object.freeze({
        color: '#fff',
        backgroundColor: theme.palette.primary.main,
        border: `2px solid ${theme.palette.primary.main}`,
    }),
    stepContent: Object.freeze({
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
    }),
    stepSubtitle: Object.freeze({
        fontSize: '0.75rem',
        color: COLOURS.DARK_GREY,
        marginTop: theme.spacing.unit * 0.5,
    }),
    stepTime: Object.freeze({
        fontSize: '0.75rem',
        color: COLOURS.DARK_GREY,
        marginTop: theme.spacing.unit,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: theme.spacing.unit * 0.5,
        fontWeight: 500,
    }),
    connectorActive: {
        '& $connectorLine': {
            borderColor: theme.palette.primary.main,
        },
    },
    connectorCompleted: {
        '& $connectorLine': {
            borderColor: theme.palette.primary.main,
        },
    },
    connectorLine: {
        borderColor: COLOURS.GREY,
        borderTopWidth: 2,
        borderTopStyle: 'solid',
        transition: theme.transitions.create('border-color'),
    },
});

export default stepperStyles;
