import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        supportLink: Object.freeze({
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
    });
