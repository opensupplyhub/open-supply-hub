export default theme =>
    Object.freeze({
        root: Object.freeze({
            background: theme.palette.background.grey,
            padding: '48px 5% 120px 5%',
        }),
        loadingRoot: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '60vh',
            background: theme.palette.background.grey,
        }),
        errorList: Object.freeze({
            listStyle: 'none',
            padding: theme.spacing.unit * 2,
        }),
        errorItem: Object.freeze({
            color: theme.palette.error.main,
            marginBottom: theme.spacing.unit,
        }),
    });
