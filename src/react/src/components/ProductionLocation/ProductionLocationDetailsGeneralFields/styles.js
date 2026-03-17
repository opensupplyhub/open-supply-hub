import { getTypographyStyles } from '../../../util/typographyStyles';

export default theme => {
    const spacing = theme.spacing.unit ?? 8;
    const typography = getTypographyStyles(theme);

    return Object.freeze({
        container: Object.freeze({
            padding: '20px',
            backgroundColor: 'white',
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        }),
        titleRow: Object.freeze({
            gap: '8px',
            marginBottom: '12px',
            alignItems: 'center',
        }),
        titleIcon: Object.freeze({
            color: theme.palette.text.secondary,
        }),
        title: Object.freeze({
            ...typography.sectionTitle,
            marginTop: 0,
            marginBottom: 0,
            marginRight: 0,
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
