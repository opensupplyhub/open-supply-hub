import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        contributionCard: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            padding: '16px',
            marginBottom: '8px',
        }),
        contributionCardPromoted: Object.freeze({
            backgroundColor: '#F8F5FB',
        }),
        contributionValueContainer: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
        }),
        contributionValue: Object.freeze({
            fontWeight: 600,
            fontSize: '1.125rem',
            lineHeight: 1.4,
            color: COLOURS.NEAR_BLACK,
            marginBottom: '8px',
        }),
        contributionValuePromoted: Object.freeze({
            fontSize: '1.25rem',
        }),
        contributionSourceContainer: Object.freeze({
            maxWidth: '45%',
        }),
        contributionSource: Object.freeze({
            fontSize: '1rem',
            lineHeight: 1.4,
            color: COLOURS.PURPLE,
        }),
        contributionSourcePromoted: Object.freeze({
            fontSize: '1.1rem',
        }),
        contributionSourceLink: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
            fontSize: '1rem',
            lineHeight: 1.4,
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            cursor: 'pointer',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        contributionSourceLinkPromoted: Object.freeze({
            fontSize: '1.1rem',
        }),
        contributionSourceIcon: Object.freeze({
            fontSize: '0.875rem',
            color: COLOURS.PURPLE,
            marginLeft: '4px',
        }),
        contributionSourceIconPromoted: Object.freeze({
            fontSize: '1rem',
        }),
        contributionMetaContainer: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            fontSize: '0.875rem',
            color: COLOURS.DARK_GREY,
            gap: '8px',
            maxWidth: '45%',
        }),
        contributionLink: Object.freeze({
            padding: '4px',
            color: COLOURS.DARK_GREY,
        }),
        dateWithIcon: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            fontSize: '1rem',
        }),
        dateWithIconPromoted: Object.freeze({
            fontSize: '1.1rem',
        }),
        dateIcon: Object.freeze({
            marginRight: '4px',
            marginTop: '2px',
            fontSize: '0.8125rem',
            color: COLOURS.DARK_GREY,
        }),
        dateIconPromoted: Object.freeze({
            fontSize: '0.9rem',
        }),
    });
