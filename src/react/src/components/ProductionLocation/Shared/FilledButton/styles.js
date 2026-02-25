export default theme =>
    Object.freeze({
        button: Object.freeze({
            backgroundColor: theme.palette.action.main,
            color: 'rgb(0, 0, 0)',
            border: 'none',
            borderRadius: 0,
            padding: '8px 16px',
            fontWeight: 900,
            boxShadow: 'none',
            '&:hover': Object.freeze({
                backgroundColor: theme.palette.action.dark,
                boxShadow: 'none',
            }),
        }),
    });
