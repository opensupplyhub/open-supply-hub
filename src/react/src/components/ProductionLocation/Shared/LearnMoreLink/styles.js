import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        paragraph: Object.freeze({
            marginTop: '8px',
            marginBottom: '0px',
        }),
        link: Object.freeze({
            color: COLOURS.PURPLE,
            textDecoration: 'none',
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
    });
