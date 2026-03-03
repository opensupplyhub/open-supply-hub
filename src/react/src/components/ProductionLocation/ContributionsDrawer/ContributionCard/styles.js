import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        contributionCard: Object.freeze({
            backgroundColor: COLOURS.WHITE,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            borderRadius: 6,
            padding: 16,
            marginBottom: 8,
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
            fontSize: '18px',
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
        contributionMetaContainer: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-end',
            fontSize: 14,
            color: COLOURS.DARK_GREY,
            gap: 8,
            maxWidth: '45%',
        }),
        contributionLink: Object.freeze({
            padding: 4,
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
            marginRight: 4,
            marginTop: '2px',
            fontSize: '13px',
            color: COLOURS.DARK_GREY,
        }),
        dateIconPromoted: Object.freeze({
            fontSize: '0.9rem',
        }),
    });
