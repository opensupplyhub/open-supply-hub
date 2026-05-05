import { getTypographyStyles } from '../../../../util/typographyStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            padding: '0 20px 0 0',
        }),
        title: Object.freeze({
            ...typography.formLabelTight,
            fontSize: '3rem',
            fontWeight: 700,
            marginTop: 0,
            marginBottom: spacing,
            [theme.breakpoints.down('sm')]: {
                fontSize: '2.5rem',
                lineHeight: 1,
            },
        }),
        titleAccent: Object.freeze({
            ...typography.bodyText,
            fontSize: '1.15rem',
        }),
    });
};
