import COLOURS from '../../../util/COLOURS';
import { makeFilterStyles } from '../../../util/styles';

export default theme =>
    Object.freeze({
        ...makeFilterStyles(theme),
        root: Object.freeze({
            position: 'relative',
        }),
        searchInputWrapper: Object.freeze({
            position: 'relative',
        }),
        searchIcon: Object.freeze({
            position: 'absolute',
            left: '10px',
            top: '50%',
            transform: 'translateY(-50%)',
            pointerEvents: 'none',
            display: 'flex',
            alignItems: 'center',
        }),
        searchInput: Object.freeze({
            width: '100%',
            boxSizing: 'border-box',
            border: `1px solid ${COLOURS.GREY}`,
            fontSize: '16px',
            padding: '8px 16px 8px 36px',
            fontWeight: 400,
            fontFamily: theme.typography.fontFamily,
            '&:focus': {
                border: `1px solid ${COLOURS.DARK_PURPLE}`,
                outline: 'none',
                boxShadow: `0px 0px 8px -1px ${COLOURS.LIGHT_PURPLE}`,
            },
        }),
        chips: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            gap: '6px',
            marginTop: '10px',
        }),
        chip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '12px',
            background: COLOURS.LIGHT_LAVENDER,
            color: COLOURS.DARK_PURPLE,
            borderRadius: '4px',
            padding: '4px 8px',
            maxWidth: '100%',
        }),
        chipLabel: Object.freeze({
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
        }),
        chipContext: Object.freeze({
            opacity: 0.7,
            flexShrink: 0,
        }),
        chipRemove: Object.freeze({
            cursor: 'pointer',
            fontSize: '16px',
            lineHeight: 1,
            flexShrink: 0,
            border: 'none',
            background: 'transparent',
            color: 'inherit',
            padding: 0,
        }),
        resultsPanel: Object.freeze({
            marginTop: '10px',
            background: COLOURS.HOVER_GREY,
            border: `1px solid ${COLOURS.GREY}`,
            borderRadius: '4px',
            overflow: 'hidden',
            maxHeight: '280px',
            overflowY: 'auto',
        }),
        resultRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '9px 12px',
            cursor: 'pointer',
            borderTop: `1px solid ${COLOURS.GREY}`,
            '&:first-of-type': {
                borderTop: 'none',
            },
        }),
        resultRowSelected: Object.freeze({
            background: COLOURS.LIGHT_LAVENDER,
        }),
        resultRowIcon: Object.freeze({
            fontSize: '18px',
            color: COLOURS.DARK_GREY,
            flexShrink: 0,
        }),
        resultRowIconSelected: Object.freeze({
            color: COLOURS.DARK_PURPLE,
        }),
        resultRowLabel: Object.freeze({
            fontSize: '14px',
            color: COLOURS.BLACK,
            flex: 1,
            minWidth: 0,
        }),
        resultRowLabelParent: Object.freeze({
            fontWeight: 700,
        }),
        resultRowCount: Object.freeze({
            marginLeft: 'auto',
            fontSize: '11px',
            color: COLOURS.MEDIUM_GREY,
            background: COLOURS.WHITE,
            borderRadius: '4px',
            padding: '2px 7px',
            flexShrink: 0,
        }),
        highlight: Object.freeze({
            background: COLOURS.LIGHT_LAVENDER_BORDER,
            color: COLOURS.DARK_PURPLE,
            borderRadius: '3px',
            padding: '0 1px',
        }),
        emptyResults: Object.freeze({
            padding: '16px',
            fontSize: '14px',
            color: COLOURS.MEDIUM_GREY,
        }),
        hint: Object.freeze({
            fontSize: '12px',
            color: COLOURS.MEDIUM_GREY,
            margin: '10px 2px 0',
        }),
    });
