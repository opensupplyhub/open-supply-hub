import COLOURS from '../../util/COLOURS';

const registerFormSuccessBannerStyles = Object.freeze({
    wrapper: Object.freeze({
        backgroundColor: COLOURS.PURPLE_TINT,
        border: `1px solid ${COLOURS.PURPLE}`,
        borderRadius: '4px',
        padding: '16px 20px',
        marginTop: '24px',
        marginBottom: '48px',
    }),
    heading: Object.freeze({
        margin: '0 0 12px',
        fontWeight: 'bold',
    }),
    list: Object.freeze({
        margin: 0,
        paddingLeft: '20px',
    }),
    listItem: Object.freeze({
        marginBottom: '8px',
    }),
});

export default registerFormSuccessBannerStyles;
