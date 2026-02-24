export default theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            [theme.breakpoints.up('md')]: {
                marginRight: theme.spacing.unit,
            },
        }),
        title: Object.freeze({
            marginBottom: theme.spacing.unit,
        }),
    });
