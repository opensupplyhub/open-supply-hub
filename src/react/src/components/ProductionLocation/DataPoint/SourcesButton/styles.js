import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        button: Object.freeze({
            textTransform: 'none',
            fontWeight: 600,
            fontSize: '1.125rem',
            lineHeight: 1.7,
            padding: '0px',
            minHeight: '0px',
            color: COLOURS.PURPLE,
            '&:hover': Object.freeze({
                backgroundColor: 'transparent',
                textDecoration: 'underline',
            }),
        }),
    });
