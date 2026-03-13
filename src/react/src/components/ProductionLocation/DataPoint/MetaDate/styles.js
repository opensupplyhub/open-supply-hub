import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        root: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
        }),
        icon: Object.freeze({
            marginRight: '4px',
            fontSize: '0.8125rem',
            color: COLOURS.DARK_GREY,
            marginTop: '3px',
        }),
        text: Object.freeze({
            fontSize: '1.125rem',
            lineHeight: 1.7,
            color: COLOURS.DARK_GREY,
        }),
    });
