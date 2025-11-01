import COLOURS from '../../../../../util/COLOURS';

const formLabel = Object.freeze({
    margin: '24px 0 8px 0',
    fontSize: '21px',
    fontWeight: 600,
});

const contactInfoStepStyles = theme =>
    Object.freeze({
        formLabel: Object.freeze({
            ...formLabel,
        }),
        formLabelRoot: Object.freeze({
            ...formLabel,
            marginTop: 0,
        }),
        fieldContainer: Object.freeze({
            position: 'relative',
            maxWidth: '528px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
        }),
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
        boxWarningContainer: {
            backgroundColor: COLOURS.LIGHT_RED,
            padding: theme.spacing.unit * 1.5,
            display: 'flex',
            alignItems: 'center',
            marginTop: '20px',
        },
        sectionTitle: Object.freeze({
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        sectionDescription: Object.freeze({
            margin: '0 0 20px 0',
            fontSize: '18px',
        }),
        sectionTitleContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: `20px`,
        }),
        separator: {
            margin: '40px 0 15px 0',
            color: COLOURS.BLACK,
        },
        gridSpacing: Object.freeze({
            marginTop: theme.spacing.unit * 2,
        }),
        betaBadge: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            padding: '2px 6px',
            borderRadius: 9999,
            fontSize: '10px',
            fontWeight: 700,
            color: '#ffffff',
            backgroundImage: `linear-gradient(to right, ${COLOURS.PURPLE_GRADIENT_FROM}, ${COLOURS.PINK_GRADIENT_TO})`,
            cursor: 'pointer',
            position: 'absolute',
            top: 57,
            right: 13,
            zIndex: 2,
        }),
        notchedOutlineStyles: Object.freeze({
            borderRadius: 0,
        }),
        errorWrapStyles: Object.freeze({
            marginTop: '8px',
        }),
        inputStyles: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            lineHeight: '22px',
            padding: '16px',
        }),
    });

export default contactInfoStepStyles;
