import { getTypographyStyles } from '../../../../util/typographyStyles';

export default theme => {
    const spacing = theme.spacing.unit ?? 8;
    const typography = getTypographyStyles(theme);

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
            ...typography.sectionTitle,
            marginTop: 0,
            marginBottom: 0,
            marginRight: `2px`,
            fontWeight: 'bold',
        }),
        infoButton: Object.freeze({
            marginLeft: spacing * -0.5,
            color: theme.palette.text.secondary,
        }),
        description: Object.freeze({
            marginBottom: spacing * 2,
            fontSize: '1.25rem',
        }),
    });
};
