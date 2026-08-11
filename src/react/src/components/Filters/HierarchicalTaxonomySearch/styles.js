import COLOURS from '../../../util/COLOURS';
import {
    makeFilterMultiValueChipStyles,
    makeFilterStyles,
} from '../../../util/styles';

const resultRowBase = Object.freeze({
    display: 'flex',
    alignItems: 'center',
    gap: '5px',
    cursor: 'pointer',
    borderTop: `1px solid ${COLOURS.GREY}`,
    '&:first-of-type': {
        borderTop: 'none',
    },
    '&:hover': {
        background: COLOURS.LIGHT_LAVENDER,
    },
});

export default function taxonomySearchStyles(theme) {
    return Object.freeze({
        ...makeFilterStyles(theme),
        ...makeFilterMultiValueChipStyles(),
        root: Object.freeze({
            position: 'relative',
        }),
        searchControl: Object.freeze({
            position: 'relative',
            display: 'flex',
            alignItems: 'flex-start',
            boxSizing: 'border-box',
            border: `1px solid ${COLOURS.GREY}`,
            minHeight: '38px',
            padding: '2px 8px 2px 36px',
            cursor: 'text',
            background: COLOURS.WHITE,
        }),
        searchControlFocused: Object.freeze({
            border: `1px solid ${COLOURS.DARK_PURPLE}`,
            boxShadow: `0px 0px 8px -1px ${COLOURS.LIGHT_PURPLE}`,
        }),
        searchIcon: Object.freeze({
            position: 'absolute',
            left: '10px',
            top: '8px',
            pointerEvents: 'none',
            display: 'flex',
            alignItems: 'center',
        }),
        searchValueContainer: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            flex: 1,
            minWidth: 0,
            padding: '2px 0',
        }),
        searchInput: Object.freeze({
            border: 'none',
            outline: 'none',
            flex: '1 1 60px',
            minWidth: '60px',
            fontSize: '16px',
            padding: '4px 0',
            fontWeight: 400,
            fontFamily: theme.typography.fontFamily,
            background: 'transparent',
        }),
        resultsPanel: Object.freeze({
            marginTop: '10px',
            marginBottom: 0,
            padding: 0,
            listStyle: 'none',
            background: COLOURS.WHITE,
            border: `1px solid ${COLOURS.GREY}`,
            borderRadius: 0,
            overflow: 'hidden',
            maxHeight: '280px',
            overflowY: 'auto',
        }),
        resultRowItem: Object.freeze({
            margin: 0,
            padding: 0,
        }),
        resultRowParent: Object.freeze({
            ...resultRowBase,
            padding: '5px 12px',
        }),
        resultRowChild: Object.freeze({
            ...resultRowBase,
            padding: '1px 12px',
        }),
        resultRowSelected: Object.freeze({
            background: COLOURS.LIGHT_LAVENDER,
        }),
        chevronButton: Object.freeze({
            display: 'flex',
            padding: 0,
            flexShrink: 0,
        }),
        resultRowLabel: Object.freeze({
            fontSize: '14px',
            color: COLOURS.BLACK,
            flex: 1,
            minWidth: 0,
            textAlign: 'left',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer',
            padding: 0,
            fontFamily: 'inherit',
        }),
        resultRowLabelParent: Object.freeze({
            fontSize: '16px',
            fontWeight: 700,
            color: COLOURS.BLACK,
            flex: 1,
            minWidth: 0,
            textAlign: 'left',
            border: 'none',
            background: 'transparent',
            cursor: 'pointer',
            padding: 0,
            fontFamily: 'inherit',
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
}
