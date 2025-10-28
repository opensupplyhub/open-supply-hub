import COLOURS from '../../../../../util/COLOURS';

const businessStepStyles = theme =>
    Object.freeze({
        card: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            boxShadow: 'none',
            border: `1px solid ${COLOURS.GREY}`,
        }),
        content: Object.freeze({
            padding: theme.spacing.unit * 3,
        }),
        section: Object.freeze({
            marginBottom: theme.spacing.unit * 3,
        }),
        sectionTitle: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            fontWeight: 600,
            fontSize: '1rem',
        }),
        field: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
        disabledField: Object.freeze({
            backgroundColor: '#f5f5f5',
            cursor: 'not-allowed',
        }),
        linkField: Object.freeze({
            display: 'block',
            width: '100%',
            padding: theme.spacing.unit * 2,
            backgroundColor: '#f5f5f5',
            border: '1px solid rgba(0, 0, 0, 0.23)',
            borderRadius: '4px',
            color: '#1976d2',
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
                backgroundColor: '#eeeeee',
            },
        }),
        verificationSection: Object.freeze({
            marginTop: theme.spacing.unit * 3,
            marginBottom: theme.spacing.unit * 2,
        }),
        selectStyles: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
        errorText: Object.freeze({
            color: theme.palette.error.main,
            fontSize: '0.75rem',
            marginTop: theme.spacing.unit,
            marginLeft: theme.spacing.unit * 2,
        }),
        helperText: Object.freeze({
            marginTop: theme.spacing.unit,
            marginLeft: 0,
        }),
        importantNotice: Object.freeze({
            backgroundColor: '#fff3e0',
            border: '1px solid #ffb74d',
            borderRadius: '4px',
            padding: theme.spacing.unit * 2,
            marginTop: theme.spacing.unit * 2,
            display: 'flex',
            alignItems: 'flex-start',
        }),
        noticeIcon: Object.freeze({
            color: '#f57c00',
            marginRight: theme.spacing.unit,
            fontSize: '1.2rem',
        }),
        noticeText: Object.freeze({
            fontSize: '0.875rem',
            lineHeight: 1.5,
        }),
        uploaderContainer: Object.freeze({
            marginTop: theme.spacing.unit * 2,
        }),
    });

export default businessStepStyles;
