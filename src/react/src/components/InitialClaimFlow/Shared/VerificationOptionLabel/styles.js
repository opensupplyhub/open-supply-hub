import COLOURS from '../../../../util/COLOURS';

const tag = Object.freeze({
    flexShrink: 0,
    padding: '0 8px',
    borderRadius: '10px',
    fontSize: '14px',
    fontWeight: 700,
    whiteSpace: 'nowrap',
});

// The tag sits to the right of the option's text and drops under it when
// the dropdown is too narrow for both.
const styles = () =>
    Object.freeze({
        root: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'baseline',
            justifyContent: 'space-between',
            gap: '4px 12px',
        }),
        preferredTag: Object.freeze({
            ...tag,
            color: COLOURS.GREEN_TEXT,
            backgroundColor: COLOURS.LIGHT_GREEN,
        }),
        canDelayTag: Object.freeze({
            ...tag,
            color: COLOURS.AMBER_800,
            backgroundColor: COLOURS.LIGHT_AMBER,
        }),
    });

export default styles;
