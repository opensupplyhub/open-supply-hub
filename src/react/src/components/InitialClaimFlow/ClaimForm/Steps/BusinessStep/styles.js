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
        card: Object.freeze({
            boxShadow: 'none',
            borderRadius: '0',
            marginBottom: '12px',
        }),
        content: Object.freeze({
            padding: 0,
            '&:last-child': {
                padding: 0,
            },
        }),
        productionLocationSection: Object.freeze({
            marginBottom: theme.spacing.unit * 3,
        }),
        sectionTitle: Object.freeze({
            fontSize: '20px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: '20px',
        }),
        verificationSectionTitle: Object.freeze({
            marginBottom: '0',
        }),
        fieldLabel: Object.freeze({
            fontSize: '17px',
            color: COLOURS.BLACK,
            fontWeight: 600,
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
        verificationSection: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
        verificationDescription: Object.freeze({
            fontSize: '16px',
            color: COLOURS.DARK_GREY,
            fontWeight: 500,
            marginBottom: theme.spacing.unit * 2,
        }),
        notchedOutlineStyles: Object.freeze({
            borderRadius: '0',
        }),
        selectStyles: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
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
        warningBox: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREY,
            padding: theme.spacing.unit * 1.5,
            alignItems: 'center',
        }),
    });

export default businessStepStyles;
