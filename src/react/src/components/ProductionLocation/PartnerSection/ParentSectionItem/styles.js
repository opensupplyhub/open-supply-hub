export default theme =>
    Object.freeze({
        container: Object.freeze({
            backgroundColor: 'white',
            marginBottom: theme.spacing.unit,
        }),
        title: Object.freeze({
            marginBottom: theme.spacing.unit,
        }),
        switchWrapper: Object.freeze({
            zIndex: 1,
        }),
    });
