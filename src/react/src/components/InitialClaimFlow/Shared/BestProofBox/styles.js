import COLOURS from '../../../../util/COLOURS';

// Light purple, so green stays for the upload area and red for the
// Important notes. Placement is left to the parent (see FieldWithTip).
const styles = theme =>
    Object.freeze({
        box: Object.freeze({
            boxSizing: 'border-box',
            width: '100%',
            backgroundColor: COLOURS.PURPLE_TINT,
            border: `1px solid ${COLOURS.LIGHT_PURPLE}`,
            padding: theme.spacing.unit * 1.5,
        }),
        title: Object.freeze({
            fontSize: '18px',
            fontWeight: theme.typography.fontWeightSemiBold,
        }),
        detail: Object.freeze({
            fontSize: '16px',
        }),
        delay: Object.freeze({
            fontSize: '16px',
            color: COLOURS.DARK_GREY,
        }),
    });

export default styles;
