import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        dateWithIcon: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            fontSize: '16px',
            color: COLOURS.DARK_GREY,
        }),
        dateIcon: Object.freeze({
            marginRight: '4px',
            marginTop: '2px',
            fontSize: '13px',
            color: COLOURS.DARK_GREY,
        }),
    });
