import COLOURS from '../../../../util/COLOURS';

const submissionErrorsBannerStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            maxWidth: '1071px',
            boxSizing: 'border-box',
            backgroundColor: COLOURS.LIGHT_RED,
            padding: theme.spacing.unit * 1.5,
            display: 'flex',
            alignItems: 'flex-start',
            marginTop: '20px',
        }),
        content: Object.freeze({
            width: '100%',
        }),
        text: Object.freeze({
            fontSize: '18px',
            display: 'inline-flex',
            alignItems: 'center',
            flexWrap: 'wrap',
        }),
        warningIcon: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            marginRight: theme.spacing.unit,
            fontSize: 16,
            marginTop: '2px',
        }),
        textIcon: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginRight: theme.spacing.unit,
        }),
        errorList: Object.freeze({
            margin: `${theme.spacing.unit}px 0 0 ${theme.spacing.unit * 4}px`,
            padding: 0,
            fontSize: '16px',
            color: COLOURS.DARK_GREY,
        }),
    });

export default submissionErrorsBannerStyles;
