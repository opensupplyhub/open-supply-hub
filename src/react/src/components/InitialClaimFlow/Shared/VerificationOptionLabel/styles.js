import COLOURS from '../../../../util/COLOURS';

const tag = Object.freeze({
    flexShrink: 0,
    marginTop: '2px',
    padding: '0 8px',
    borderRadius: '10px',
    fontSize: '14px',
    fontWeight: 700,
    whiteSpace: 'nowrap',
});

// The tag always sits at the right edge, level with the first line of the
// option's text, so the tags line up in one column. Long text wraps beside
// the tag, never under it.
const styles = () =>
    Object.freeze({
        root: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: '12px',
        }),
        label: Object.freeze({
            flex: '1 1 auto',
            minWidth: 0,
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
