import COLOURS from '../../../../util/COLOURS';

export default () =>
    Object.freeze({
        root: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
        }),
        personIcon: Object.freeze({
            marginRight: '4px',
            marginTop: '2px',
            fontSize: '1rem',
            color: COLOURS.DARK_GREY,
        }),
        name: Object.freeze({
            fontSize: '1.125rem',
            lineHeight: 1.7,
            color: COLOURS.DARK_GREY,
        }),
        nameLink: Object.freeze({
            textDecoration: 'none',
            cursor: 'pointer',
            fontWeight: 500,
            '&:hover': Object.freeze({
                textDecoration: 'underline',
            }),
        }),
    });
