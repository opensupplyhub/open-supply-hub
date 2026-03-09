export default theme =>
    Object.freeze({
        root: Object.freeze({
            paddingTop: theme.spacing.unit * 2,
        }),
        title: Object.freeze({
            marginBottom: theme.spacing.unit,
        }),
        description: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
    });
