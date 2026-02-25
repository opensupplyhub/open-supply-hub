export default () =>
    Object.freeze({
        button: Object.freeze({
            backgroundColor: 'transparent',
            color: 'rgba(0, 0, 0, 0.87)',
            border: '1px solid rgb(13, 17, 40)',
            borderRadius: 0,
            padding: '8px 16px',
            fontWeight: 900,
            boxShadow: 'none',
            '&:hover': Object.freeze({
                backgroundColor: 'rgba(0, 0, 0, 0.08)',
                boxShadow: 'none',
            }),
        }),
    });
