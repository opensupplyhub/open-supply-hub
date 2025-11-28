import COLOURS from '../../../../util/COLOURS';

const importantNoteStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            maxWidth: '1071px',
            width: '100%',
            backgroundColor: COLOURS.LIGHT_RED,
            padding: theme.spacing.unit * 1.5,
        }),
        text: Object.freeze({
            fontSize: '18px',
            display: 'inline-flex',
            alignItems: 'center',
            flexWrap: 'wrap',
        }),
        icon: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            marginRight: theme.spacing.unit,
            fontSize: 16,
            flexShrink: 0,
        }),
        iconWrapper: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            marginRight: theme.spacing.unit,
            flexShrink: 0,
        }),
    });

export default importantNoteStyles;
