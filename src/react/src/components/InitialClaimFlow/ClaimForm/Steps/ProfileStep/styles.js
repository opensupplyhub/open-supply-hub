import COLOURS from '../../../../../util/COLOURS';

export const profileStepStyles = theme =>
    Object.freeze({
        separator: Object.freeze({
            margin: '40px 0 15px 0',
            color: COLOURS.BLACK,
        }),
        sectionContainer: Object.freeze({}),
        sectionTitleContainer: Object.freeze({
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: 'center',
            marginTop: `20px`,
        }),
        sectionTitle: Object.freeze({
            fontSize: '24px',
            fontWeight: theme.typography.fontWeightSemiBold,
            marginBottom: theme.spacing.unit * 1.5,
        }),
        sectionDescription: Object.freeze({
            margin: '0',
            fontSize: '18px',
        }),
        fieldContainer: Object.freeze({
            position: 'relative',
            maxWidth: '528px',
            width: '100%',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
            '&:first-child': {
                marginRight: '15px',
            },
        }),
        doubleFieldContainer: Object.freeze({
            display: 'flex',
            [theme.breakpoints.down('md')]: {
                flexDirection: 'column',
            },
        }),
        formLabel: Object.freeze({
            margin: '24px 0 8px 0',
            fontSize: '21px',
            fontWeight: 600,
        }),
        inputStyles: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
            lineHeight: '22px',
            padding: '16px',
        }),
        notchedOutlineStyles: Object.freeze({
            borderRadius: '0',
        }),
        errorWrapStyles: Object.freeze({
            marginTop: '8px',
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
            zIndex: 1,
        }),
        betaBadgeColumn: Object.freeze({
            top: '80px',
        }),
        betaBadgeColumnWithHint: Object.freeze({
            top: '105px',
        }),
        textareaFieldContainer: Object.freeze({
            position: 'relative',
            maxWidth: '1071px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
        }),
        multilineInputStyles: Object.freeze({
            padding: '0',
        }),
        emissionsEstimateContainer: Object.freeze({
            marginTop: '24px',
            maxWidth: '1071px',
        }),
        sectionIconWrapper: Object.freeze({
            padding: theme.spacing.unit,
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginRight: theme.spacing.unit * 1.5,
        }),
        blueBg: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
        }),
        amberBg: Object.freeze({
            backgroundColor: '#fff8e1',
        }),
        purpleBg: Object.freeze({
            backgroundColor: COLOURS.LIGHT_PURPLE_BG,
        }),
        sectionIcon: Object.freeze({
            fontSize: '1.25rem',
        }),
        blueIcon: Object.freeze({
            color: COLOURS.MATERIAL_BLUE,
        }),
        amberIcon: Object.freeze({
            color: '#f57c00',
        }),
        purpleIcon: Object.freeze({
            color: COLOURS.DARK_PURPLE,
        }),
        greenIcon: Object.freeze({
            color: COLOURS.DARK_MATERIAL_GREEN,
        }),
        greenBg: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREEN,
        }),
        helpIcon: Object.freeze({
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
            marginLeft: theme.spacing.unit / 2,
        }),
        helpIconButton: Object.freeze({
            padding: 0,
            '&:hover': {
                backgroundColor: 'transparent',
            },
        }),
        tooltip: Object.freeze({
            fontSize: '14px',
            backgroundColor: COLOURS.WHITE,
            color: 'rgba(0, 0, 0, 0.87)',
            border: `1px solid ${COLOURS.GREY}`,
            padding: theme.spacing.unit * 1.5,
            maxWidth: 300,
        }),
    });

export default profileStepStyles;
