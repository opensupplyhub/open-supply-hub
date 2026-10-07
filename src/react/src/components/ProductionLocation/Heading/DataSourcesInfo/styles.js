import COLOURS from '../../../../util/COLOURS';

/*
The data labels legend is explanatory chrome, not facility content, so it sits
beside the OS ID rather than under it and is typed well below the page's
section headings. See OSDEV-3239.

It deliberately does not build on getTypographyStyles: that scale starts at
16px and exists for page content, so every step would have to be overridden
here. The sizes the legend does use are named below instead, so there is still
one place to change them.
*/
const TITLE_SIZE = '11px';
const TEXT_SIZE = '12px';
const ICON_SIZE = 12;
const CHEVRON_SIZE = 14;
const PANEL_MIN_HEIGHT = 108;
const SLIDE_PADDING = '12px 14px';
const SLIDE_EASE = 'cubic-bezier(.4, 0, .2, 1)';

export default theme => {
    const spacing = theme.spacing.unit ?? 8;
    const panelBorder = `1px solid ${COLOURS.LIGHT_BORDER_GREY}`;

    const colouredIcon = colour =>
        Object.freeze({
            flexShrink: 0,
            width: ICON_SIZE,
            height: ICON_SIZE,
            fontSize: ICON_SIZE,
            color: colour,
        });
    const colouredLabel = colour =>
        Object.freeze({
            fontSize: TEXT_SIZE,
            fontWeight: 700,
            color: colour,
        });

    /*
    Both controls in the panel are text buttons: no chrome of their own, and
    they take their colour from the surrounding legend.
    */
    const textButton = Object.freeze({
        display: 'flex',
        alignItems: 'center',
        alignSelf: 'flex-start',
        background: 'none',
        border: 'none',
        margin: 0,
        padding: 0,
        font: 'inherit',
        textAlign: 'left',
        cursor: 'pointer',
        color: theme.palette.text.secondary,
        '&:hover': {
            color: theme.palette.text.primary,
        },
    });

    return Object.freeze({
        /*
        A single-cell grid with both slides stacked in it, so the panel is
        always as tall as the taller slide. That keeps the height stable while
        sliding (nothing below the row shifts) without ever clipping content,
        which a fixed height plus absolute slides could not do.
        */
        container: Object.freeze({
            display: 'grid',
            overflow: 'hidden',
            minHeight: PANEL_MIN_HEIGHT,
            backgroundColor: COLOURS.LIGHT_GREY,
            /*
            The OS ID panel carries the purple fill and the row carries the
            outer border, so the legend contributes only the divider between
            the two: above it when stacked, beside it from md up.
            */
            borderTop: panelBorder,
            [theme.breakpoints.up('md')]: {
                borderTop: 0,
                borderLeft: panelBorder,
            },
        }),
        /*
        Each slide fills the shared cell and moves by a percentage of its own
        width, so nothing is ever wider than the element clipping it.
        Visibility is swapped only once the slide has finished moving, which
        keeps the off-screen copy out of find-in-page and the accessibility
        tree without cutting the animation short.
        */
        slide: Object.freeze({
            gridArea: '1 / 1',
            minWidth: 0,
            boxSizing: 'border-box',
            padding: SLIDE_PADDING,
            display: 'flex',
            flexDirection: 'column',
            /*
            `safe` so that content taller than the panel can never be pushed
            above the top edge where it cannot be reached. Browsers without
            `safe` fall back to flex-start, which is also fine.
            */
            justifyContent: 'safe center',
            transition: `transform .32s ${SLIDE_EASE}, visibility 0s`,
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
        /* Hidden only after the slide has moved out of view. */
        slideHidden: Object.freeze({
            visibility: 'hidden',
            transitionDelay: '0s, .32s',
            '@media (prefers-reduced-motion: reduce)': {
                transitionDelay: '0s',
            },
        }),
        titleRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${spacing * 0.5}px`,
            marginBottom: spacing,
        }),
        sectionTitle: Object.freeze({
            fontSize: TITLE_SIZE,
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
                fontSize: CHEVRON_SIZE,
            },
            '&:hover': {
                color: theme.palette.text.primary,
            },
        }),
        list: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
            gap: `${spacing * 0.25}px`,
        }),
        item: Object.freeze({
            ...textButton,
            gap: `${spacing}px`,
            padding: `${spacing * 0.25}px 0`,
            fontSize: TEXT_SIZE,
            fontWeight: 500,
        }),
        backButton: Object.freeze({
            ...textButton,
            gap: `${spacing * 0.25}px`,
            marginBottom: spacing * 0.5,
            fontSize: TITLE_SIZE,
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '.04em',
        }),
        /*
        No colour of its own, so it follows the hover state of the button it
        sits in rather than staying grey while the label beside it darkens.
        */
        chevron: Object.freeze({
            flexShrink: 0,
            fontSize: CHEVRON_SIZE,
        }),
        detailTitle: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${spacing}px`,
            marginBottom: spacing * 0.5,
        }),
        detailText: Object.freeze({
            margin: 0,
            fontSize: TEXT_SIZE,
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
        /* Applied by key from DATA_SOURCES_ITEMS in constants.js. */
        iconClaimed: colouredIcon(COLOURS.DARK_GREEN),
        iconCrowdsourced: colouredIcon(COLOURS.ORANGE),
        iconPartner: colouredIcon(COLOURS.PURPLE),
        labelClaimed: colouredLabel(COLOURS.DARK_GREEN),
        labelCrowdsourced: colouredLabel(COLOURS.ORANGE),
        labelPartner: colouredLabel(COLOURS.PURPLE),
    });
};
