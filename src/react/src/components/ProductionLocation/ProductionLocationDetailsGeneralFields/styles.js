export default theme =>
    Object.freeze({
        container: Object.freeze({
            padding: '20px',
            backgroundColor: 'white',
            [theme.breakpoints.up('md')]: {
                marginRight: theme.spacing.unit,
            },
        }),
        titleRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexDirection: 'row',
        }),
        title: Object.freeze({
            marginLeft: theme.spacing.unit,
            marginBottom: theme.spacing.unit,
        }),
        infoIcon: Object.freeze({
            marginLeft: theme.spacing.unit,
        }),
        dataList: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
        }),
    });
