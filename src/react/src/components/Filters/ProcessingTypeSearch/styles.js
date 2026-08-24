import COLOURS from '../../../util/COLOURS';
import taxonomySearchStyles from '../HierarchicalTaxonomySearch/styles';

const badgeBase = Object.freeze({
    fontSize: '11px',
    lineHeight: '16px',
    borderRadius: '3px',
    padding: '0 5px',
    whiteSpace: 'nowrap',
    flexShrink: 0,
});

export default function processingTypeSearchStyles(theme) {
    const sharedStyles = taxonomySearchStyles(theme);

    return Object.freeze({
        ...sharedStyles,
        resultsPanel: Object.freeze({
            ...sharedStyles.resultsPanel,
            maxHeight: '320px',
            '& > div:first-child > *': Object.freeze({
                borderTop: 'none',
            }),
        }),
        groupHeader: Object.freeze({
            margin: 0,
            padding: 0,
        }),
        groupHeaderLabel: Object.freeze({
            display: 'block',
            padding: '5px 12px',
            fontSize: '11px',
            fontWeight: 700,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            color: COLOURS.DARK_PURPLE,
            background: COLOURS.LIGHT_LAVENDER,
            borderTop: `1px solid ${COLOURS.GREY}`,
        }),
        resultRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            width: '100%',
            boxSizing: 'border-box',
            padding: '6px 12px',
            textAlign: 'left',
            fontFamily: 'inherit',
            background: 'transparent',
            border: 'none',
            borderTop: `1px solid ${COLOURS.GREY}`,
            cursor: 'pointer',
            '&:hover': Object.freeze({
                background: COLOURS.LIGHT_LAVENDER,
            }),
        }),
        resultRowSelected: Object.freeze({
            background: COLOURS.LIGHT_LAVENDER,
        }),
        // Rows outside the selected facility types are dimmed rather than
        // removed: facility type ranks the suggestions, it never hides them.
        resultRowDim: Object.freeze({
            opacity: 0.52,
        }),
        resultRowBody: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: '2px',
            flex: 1,
            minWidth: 0,
        }),
        resultRowTerm: Object.freeze({
            fontSize: '14px',
            color: COLOURS.BLACK,
            overflowWrap: 'anywhere',
        }),
        resultRowMeta: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '6px',
            fontSize: '11px',
            color: COLOURS.MEDIUM_GREY,
        }),
        resultRowBreadcrumb: Object.freeze({
            color: COLOURS.MEDIUM_GREY,
            overflowWrap: 'anywhere',
        }),
        notInTaxonomyBadge: Object.freeze({
            ...badgeBase,
            color: COLOURS.CROWDSOURCED_CHIP_TEXT,
            background: COLOURS.CROWDSOURCED_CHIP_BG,
            border: `1px solid ${COLOURS.AMBER_300}`,
        }),
        resultRowCount: Object.freeze({
            marginLeft: 'auto',
            alignSelf: 'center',
            fontSize: '11px',
            color: COLOURS.MEDIUM_GREY,
            flexShrink: 0,
        }),
        statusRow: Object.freeze({
            padding: '16px',
            fontSize: '14px',
            color: COLOURS.MEDIUM_GREY,
        }),
    });
}
