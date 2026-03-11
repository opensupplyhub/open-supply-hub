export default theme => {
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        root: Object.freeze({
            paddingTop: spacing * 2,
        }),
        divider: Object.freeze({
            marginBottom: spacing,
        }),
        titleRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: `${spacing}px`,
            marginBottom: spacing,
        }),
        icon: Object.freeze({
            flexShrink: 0,
        }),
        title: Object.freeze({
            marginTop: 0,
            marginBottom: 0,
        }),
        infoButton: Object.freeze({
            marginLeft: spacing * -0.5,
            color: theme.palette.text.secondary,
        }),
        description: Object.freeze({
            marginBottom: spacing * 2,
        }),
    });
};
