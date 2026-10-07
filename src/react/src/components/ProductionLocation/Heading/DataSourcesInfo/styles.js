import COLOURS from '../../../../util/COLOURS';

/*
The data labels legend is explanatory chrome, not facility content, so it is
deliberately typed well below the page's section headings and sits beside the
OS ID rather than under it. See OSDEV-3239.
*/
const PANEL_MIN_HEIGHT = 108;

export default theme => {
    const spacing = theme.spacing.unit ?? 8;
    const colouredIcon = colour =>
        Object.freeze({
            flexShrink: 0,
            width: 12,
            height: 12,
            fontSize: 12,
            color: colour,
        });
    const colouredLabel = colour =>
        Object.freeze({
            fontSize: '12px',
            fontWeight: 700,
            color: colour,
        });

    return Object.freeze({
        container: Object.freeze({
            position: 'relative',
            overflow: 'hidden',
            minHeight: PANEL_MIN_HEIGHT,
            backgroundColor: COLOURS.LIGHT_GREY,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            /*
            The OS ID panel sits above (mobile) or to the left (desktop) and
            carries its own border, so drop the touching edge to avoid a
            doubled divider line.
            */
            borderTop: 0,
            [theme.breakpoints.up('md')]: {
                borderTop: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
                borderLeft: 0,
            },
        }),
        /*
        Each slide is exactly the viewport's size and is moved by a percentage
        of its own width. Nothing is ever wider than the viewport it sits in,
        which keeps the translate off the scrollable-overflow path.
        */
        slide: Object.freeze({
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            boxSizing: 'border-box',
            padding: '12px 14px',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            overflowY: 'auto',
            transition: 'transform .32s cubic-bezier(.4, 0, .2, 1)',
            '@media (prefers-reduced-motion: reduce)': {
                transition: 'none',
            },
        }),
        slideIn: Object.freeze({
            transform: 'translateX(0)',
        }),
        slideOutLeft: Object.freeze({
            transform: 'translateX(-100%)',
        }),
        slideOutRight: Object.freeze({
            transform: 'translateX(100%)',
        }),
        titleRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${spacing * 0.5}px`,
            marginBottom: spacing * 0.75,
        }),
        sectionTitle: Object.freeze({
            fontSize: '11px',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '.05em',
            color: theme.palette.text.primary,
            margin: 0,
        }),
        infoButton: Object.freeze({
            padding: 0,
            color: theme.palette.text.secondary,
            '& svg': {
                fontSize: 14,
            },
            '&:hover': {
                color: theme.palette.text.primary,
            },
        }),
        list: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            gap: '1px',
        }),
        item: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            background: 'none',
            border: 'none',
            margin: 0,
            padding: '2px 0',
            font: 'inherit',
            fontSize: '12px',
            fontWeight: 500,
            textAlign: 'left',
            cursor: 'pointer',
            color: theme.palette.text.secondary,
            '&:hover': {
                color: theme.palette.text.primary,
            },
        }),
        itemLabel: Object.freeze({
            color: 'inherit',
        }),
        chevron: Object.freeze({
            flexShrink: 0,
            fontSize: 14,
            color: theme.palette.text.secondary,
        }),
        backButton: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            alignSelf: 'flex-start',
            gap: '2px',
            background: 'none',
            border: 'none',
            margin: `0 0 ${spacing * 0.75}px`,
            padding: 0,
            font: 'inherit',
            fontSize: '11px',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '.04em',
            cursor: 'pointer',
            color: theme.palette.text.secondary,
            '&:hover': {
                color: theme.palette.text.primary,
            },
        }),
        backChevron: Object.freeze({
            flexShrink: 0,
            fontSize: 14,
        }),
        detailTitle: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            marginBottom: spacing * 0.5,
        }),
        detailText: Object.freeze({
            margin: 0,
            fontSize: '12px',
            lineHeight: 1.5,
            color: theme.palette.text.secondary,
        }),
        learnMoreLink: Object.freeze({
            whiteSpace: 'nowrap',
            color: theme.palette.primary.main,
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            },
        }),
        iconClaimed: colouredIcon(COLOURS.DARK_GREEN),
        iconCrowdsourced: colouredIcon(COLOURS.ORANGE),
        iconPartner: colouredIcon(COLOURS.PURPLE),
        labelClaimed: colouredLabel(COLOURS.DARK_GREEN),
        labelCrowdsourced: colouredLabel(COLOURS.ORANGE),
        labelPartner: colouredLabel(COLOURS.PURPLE),
    });
};
