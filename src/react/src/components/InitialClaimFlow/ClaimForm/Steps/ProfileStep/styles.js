import COLOURS from '../../../../../util/COLOURS';

export const profileStepStyles = theme =>
    Object.freeze({
        separator: Object.freeze({
            margin: '40px 0 15px 0',
            color: COLOURS.BLACK,
        }),
        sectionContainer: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
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
            margin: '0 0 20px 0',
            fontSize: '18px',
        }),
        fieldContainer: Object.freeze({
            position: 'relative',
            maxWidth: '528px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
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
            zIndex: 2,
        }),
        textareaFieldContainer: Object.freeze({
            position: 'relative',
            maxWidth: '1252px',
            [theme.breakpoints.down('md')]: {
                maxWidth: '100%',
            },
        }),
        multilineInputStyles: Object.freeze({
            padding: '0',
        }),
        // OLD STYLES
        expansionPanel: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            boxShadow: 'none',
            border: `1px solid ${COLOURS.GREY}`,
            '&:before': {
                display: 'none',
            },
        }),
        expansionPanelSummary: Object.freeze({
            padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 2}px`,
            '&:hover': {
                backgroundColor: 'transparent',
            },
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
        greenBg: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREEN,
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
            color: COLOURS.MATERIAL_GREEN,
        }),
        sectionHeader: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
        }),
        sectionTitleWrapper: Object.freeze({
            flex: 1,
        }),
        expansionPanelDetails: Object.freeze({
            padding: `${theme.spacing.unit * 2}px ${theme.spacing.unit * 3}px ${
                theme.spacing.unit * 3
            }px`,
            display: 'block',
        }),
        field: Object.freeze({
            marginBottom: theme.spacing.unit * 3,
        }),
        fieldLabel: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            marginBottom: theme.spacing.unit,
            fontSize: '16px',
            '& .MuiTypography-root': {
                fontSize: '16px',
            },
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
        betaLabel: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            padding: '2px 10px',
            borderRadius: '12px',
            background: 'linear-gradient(90deg, #7B2CBF 0%, #E91E63 100%)',
            color: COLOURS.WHITE,
            fontSize: '12px',
            fontWeight: 600,
            marginLeft: theme.spacing.unit,
            cursor: 'pointer',
        }),
        betaIcon: Object.freeze({
            fontSize: '12px',
            marginRight: '2px',
        }),
        tooltip: Object.freeze({
            fontSize: '14px',
            backgroundColor: COLOURS.WHITE,
            color: 'rgba(0, 0, 0, 0.87)',
            border: `1px solid ${COLOURS.GREY}`,
            padding: theme.spacing.unit * 1.5,
            maxWidth: 300,
        }),
        subsectionTitle: Object.freeze({
            fontWeight: 500,
            fontSize: '16px',
            marginBottom: theme.spacing.unit * 2,
            marginTop: theme.spacing.unit * 2,
        }),
        subsectionSubtitle: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontWeight: 'normal',
        }),
    });

export const selectStyles = {
    control: provided => ({
        ...provided,
        minHeight: '56px',
        borderRadius: '4px',
        borderColor: 'rgba(0, 0, 0, 0.23)',
        '&:hover': {
            borderColor: 'rgba(0, 0, 0, 0.87)',
        },
        boxShadow: 'none',
    }),
    valueContainer: provided => ({
        ...provided,
        padding: '18.5px 14px',
    }),
    placeholder: provided => ({
        ...provided,
        color: 'rgba(0, 0, 0, 0.54)',
    }),
    input: provided => ({
        ...provided,
        margin: 0,
        padding: 0,
    }),
};
