import COLOURS from '../../../../../util/COLOURS';

const businessStepStyles = theme =>
    Object.freeze({
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
        verficationSectionTitle: Object.freeze({
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
        warningText: Object.freeze({
            fontSize: 16,
            fontWeight: 400,
        }),
        warningBoldText: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            fontWeight: 700,
        }),
        warningIconContainer: Object.freeze({
            marginRight: theme.spacing.unit,
            display: 'inline-flex',
        }),
        warningIcon: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            fontSize: 16,
        }),
    });

export default businessStepStyles;
