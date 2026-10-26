import COLOURS from '../../util/COLOURS';

const identityRecordStyles = theme =>
    Object.freeze({
        root: Object.freeze({
            maxWidth: '55rem',
            margin: '0 auto',
            padding: '2rem 1.5rem 4rem',
        }),
        centered: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            padding: '4rem 0',
        }),
        loadingText: Object.freeze({
            marginTop: '1rem',
            color: COLOURS.DARK_GREY,
        }),
        attribution: Object.freeze({
            fontSize: '0.9rem',
            color: COLOURS.DARK_GREY,
            marginBottom: '1rem',
        }),
        card: Object.freeze({
            padding: '1.5rem',
            marginBottom: '1.25rem',
        }),
        name: Object.freeze({
            fontFamily: theme.typography.fontFamily,
            fontWeight: 700,
            marginBottom: '1rem',
        }),
        heading: Object.freeze({
            fontWeight: 700,
            marginBottom: '0.75rem',
        }),
        fields: Object.freeze({
            display: 'grid',
            gridTemplateColumns: 'minmax(9rem, 14rem) 1fr',
            columnGap: '1.5rem',
            rowGap: '0.5rem',
            margin: 0,
        }),
        term: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontSize: '0.9rem',
        }),
        detail: Object.freeze({
            margin: 0,
            wordBreak: 'break-word',
        }),
        caveat: Object.freeze({
            marginTop: '1rem',
            fontSize: '0.85rem',
            color: COLOURS.DARK_GREY,
        }),
        claims: Object.freeze({
            listStyle: 'none',
            margin: 0,
            padding: 0,
        }),
        claim: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'baseline',
            gap: '0.75rem',
            padding: '0.6rem 0',
            borderBottom: `1px solid ${COLOURS.GREY}`,
        }),
        claimName: Object.freeze({
            flex: '1 1 20rem',
        }),
        claimScore: Object.freeze({
            fontSize: '0.78rem',
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            background: COLOURS.LIGHT_GREY,
            padding: '0.15rem 0.5rem',
            borderRadius: '3px',
        }),
        claimDate: Object.freeze({
            fontSize: '0.85rem',
            color: COLOURS.DARK_GREY,
        }),
        unavailable: Object.freeze({
            padding: '2rem',
        }),
        unavailableText: Object.freeze({
            marginTop: '0.75rem',
        }),
        externalLink: Object.freeze({
            color: COLOURS.NAVY_BLUE,
        }),
        locationLink: Object.freeze({
            color: COLOURS.NAVY_BLUE,
            fontWeight: 700,
        }),
        footerLink: Object.freeze({
            marginTop: '1.5rem',
        }),
    });

export default identityRecordStyles;
