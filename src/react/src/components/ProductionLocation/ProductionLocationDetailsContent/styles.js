export default theme =>
    Object.freeze({
        container: Object.freeze({
            [theme.breakpoints.up('md')]: {
                paddingLeft: '40px',
            },
        }),
        containerItem: Object.freeze({
            marginBottom: theme.spacing.unit,
        }),
    });
