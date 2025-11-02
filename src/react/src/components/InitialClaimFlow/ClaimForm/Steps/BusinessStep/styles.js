import COLOURS from '../../../../../util/COLOURS';

const formLabel = Object.freeze({
    margin: '24px 0 8px 0',
    fontSize: '21px',
    fontWeight: 600,
});

const businessStepStyles = theme =>
    Object.freeze({
        formLabel: Object.freeze({
            ...formLabel,
        }),
        formLabelRoot: Object.freeze({
            ...formLabel,
            marginTop: 0,
        }),
        formFieldContainer: Object.freeze({
            position: 'relative',
            maxWidth: '528px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
        }),
        documentUploadContainer: Object.freeze({
            maxWidth: '1252px',
        }),
        boxWarningContainer: Object.freeze({
            backgroundColor: COLOURS.LIGHT_RED,
            padding: theme.spacing.unit * 1.5,
            display: 'flex',
            alignItems: 'center',
            marginTop: '20px',
        }),
        boxWarningText: Object.freeze({
            fontSize: '18px',
            display: 'inline-flex',
            alignItems: 'center',
        }),
        warningIcon: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            marginRight: theme.spacing.unit,
            fontSize: 16,
            marginTop: '2px',
        }),
        boxWarningTextIcon: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginRight: theme.spacing.unit,
        }),
        disabledField: Object.freeze({
            cursor: 'default',
            boxSizing: 'border-box',
            padding: theme.spacing.unit * 2,
            backgroundColor: '#f5f5f5',
            fontWeight: 600,
            fontSize: '17px',
            borderRadius: '0',
        }),
        linkField: Object.freeze({
            display: 'block',
            width: '100%',
            boxSizing: 'border-box',
            padding: theme.spacing.unit * 2,
            backgroundColor: '#f5f5f5',
            border: '1px solid rgba(0, 0, 0, 0.23)',
            borderRadius: '0',
            color: '#1976d2',
            textDecoration: 'none',
            fontWeight: 600,
            fontSize: '19px',
            '&:hover': {
                textDecoration: 'underline',
                backgroundColor: '#eeeeee',
            },
        }),
        notchedOutlineStyles: Object.freeze({
            borderRadius: '0',
        }),
        errorWrapStyles: Object.freeze({
            margin: '8px 12px 0 0',
        }),
        helperText: Object.freeze({
            marginTop: theme.spacing.unit,
            marginLeft: 0,
        }),
        errorInput: Object.freeze({
            color: COLOURS.RED,
        }),
    });

export default businessStepStyles;
