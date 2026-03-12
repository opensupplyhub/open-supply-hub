export default theme => {
    const spacing = theme.spacing.unit ?? 8;

    return Object.freeze({
        container: Object.freeze({
            padding: '20px',
            backgroundColor: 'white',
            [theme.breakpoints.up('md')]: {
                marginRight: theme.spacing.unit,
            },
        }),
        titleRow: Object.freeze({
            gap: '8px',
            marginBottom: '12px',
        }),
        titleItem: Object.freeze({
            display: 'inline-flex',
        }),
        title: Object.freeze({
            lineHeight: '1.3125rem',
        }),
        infoIcon: Object.freeze({
            padding: spacing * 0.5,
            '&:hover': {
                color: theme.palette.text.primary,
                backgroundColor: theme.palette.action.hover,
            },
        }),
        dividerContainer: Object.freeze({
            marginBottom: '16px',
        }),
        dataList: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
        }),
    });
};
