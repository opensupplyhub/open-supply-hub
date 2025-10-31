import COLOURS from '../../../../../util/COLOURS';

export const profileStepStyles = theme =>
    Object.freeze({
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
        sectionTitle: Object.freeze({
            fontWeight: 600,
            fontSize: '22px',
            marginBottom: theme.spacing.unit / 2,
        }),
        sectionDescription: Object.freeze({
            fontSize: '16px',
            color: COLOURS.DARK_GREY,
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
