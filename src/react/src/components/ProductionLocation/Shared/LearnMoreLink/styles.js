import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        paragraph: Object.freeze({
            marginTop: 8,
            marginBottom: 0,
        }),
        link: Object.freeze({
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
    });
