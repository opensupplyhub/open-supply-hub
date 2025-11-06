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
            width: '100%',
            position: 'relative',
            maxWidth: '528px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
            '&:first-child': {
                marginRight: '15px',
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
            maxWidth: '1071px',
            boxSizing: 'border-box',
            backgroundColor: COLOURS.LIGHT_RED,
            padding: theme.spacing.unit * 1.5,
            display: 'flex',
            alignItems: 'center',
            marginTop: '20px',
        },
        sectionTitle: Object.freeze({
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginTop: '25px',
        }),
        sectionDescription: Object.freeze({
            fontSize: '18px',
            marginBottom: '10px',
        }),
        sectionTitleContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: 'center',
        }),
        publicInfoContainer: Object.freeze({
            boxSizing: 'border-box',
            maxWidth: '1071px',
            background: COLOURS.LIGHT_AMBER,
            padding: '10px 20px 15px 20px',
            marginTop: '15px',
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
            top: 80,
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
        switchContainer: Object.freeze({
            margin: '0 0 5px 0',
        }),
        subDescription: Object.freeze({
            marginTop: '0',
        }),
        doubleFieldContainer: Object.freeze({
            display: 'flex',
            [theme.breakpoints.down('md')]: {
                flexDirection: 'column',
            },
        }),
    });

export default contactInfoStepStyles;
