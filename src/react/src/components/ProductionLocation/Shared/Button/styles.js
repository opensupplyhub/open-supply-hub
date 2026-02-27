const commonButtonStyles = Object.freeze({
    borderRadius: 0,
    padding: '8px 16px',
    fontWeight: 900,
    boxShadow: 'none',
    '&:hover': Object.freeze({
        boxShadow: 'none',
    }),
});

export default theme =>
    Object.freeze({
        outlined: Object.freeze({
            ...commonButtonStyles,
            backgroundColor: 'transparent',
            border: '1px solid rgb(13, 17, 40)',
            '&:hover': Object.freeze({
                ...commonButtonStyles['&:hover'],
                backgroundColor: 'rgba(0, 0, 0, 0.08)',
            }),
        }),
        filled: Object.freeze({
            ...commonButtonStyles,
            backgroundColor: theme.palette.action.main,
            border: 'none',
            '&:hover': Object.freeze({
                ...commonButtonStyles['&:hover'],
                backgroundColor: theme.palette.action.dark,
            }),
        }),
    });
