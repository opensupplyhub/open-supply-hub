import COLOURS from '../../../../util/COLOURS';

const whyBetaCardStyles = theme => {
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        root: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'flex-start',
        }),
        chip: Object.freeze({
            marginBottom: spacing * 1.5,
        }),
        card: Object.freeze({
            // Indented under the chip, as in the mockup.
            marginLeft: spacing * 3,
            backgroundColor: COLOURS.BETA_CARD_BG,
            color: COLOURS.WHITE,
            borderRadius: '8px',
            padding: `${spacing * 3}px`,
            maxWidth: '520px',
        }),
        title: Object.freeze({
            color: COLOURS.WHITE,
            fontSize: '1rem',
            fontWeight: 700,
            marginBottom: spacing,
        }),
        body: Object.freeze({
            color: COLOURS.WHITE,
            fontSize: '1rem',
            lineHeight: 1.5,
            marginBottom: spacing * 1.5,
        }),
        link: Object.freeze({
            color: COLOURS.BETA_CARD_LINK,
            fontSize: '1rem',
            textDecoration: 'underline',
            '&:hover': Object.freeze({
                color: COLOURS.WHITE,
            }),
        }),
    });
};

export default whyBetaCardStyles;
