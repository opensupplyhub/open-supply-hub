export default theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: theme.palette.background.white,
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        }),
    });
