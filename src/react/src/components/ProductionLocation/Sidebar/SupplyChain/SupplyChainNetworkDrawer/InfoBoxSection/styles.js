import COLOURS from '../../../../../../util/COLOURS';

export default () =>
    Object.freeze({
        infoBox: Object.freeze({
            backgroundColor: COLOURS.EXTRA_LIGHT_BLUE,
            border: `1px solid #C0DBFE`,
            padding: '16px',
            marginBottom: '16px',
        }),
        infoBoxWithIcon: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            gap: '8px',
        }),
        infoIcon: Object.freeze({
            fontSize: '1.25rem',
            color: COLOURS.MATERIAL_BLUE,
            flexShrink: 0,
            marginTop: '2px',
            marginRight: '8px',
        }),
        infoBoxContent: Object.freeze({
            flex: 1,
        }),
        infoText: Object.freeze({
            fontSize: '1rem',
            lineHeight: 1.5,
            color: COLOURS.DARK_GREY,
        }),
        learnMoreLink: Object.freeze({
            marginTop: '8px',
            display: 'inline-flex',
            alignItems: 'center',
            color: COLOURS.MATERIAL_BLUE,
            fontSize: '1rem',
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
        learnMoreArrow: Object.freeze({
            marginLeft: '4px',
            marginTop: '2px',
        }),
    });
