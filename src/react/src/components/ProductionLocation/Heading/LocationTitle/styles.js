import { getTypographyStyles } from '../../../../util/typographyStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            backgroundColor: theme.palette.background.paper,
            marginBottom: spacing * 3,
        }),
        title: Object.freeze({
            ...typography.formLabelTight,
            fontSize: '28px',
            fontWeight: 700,
            marginTop: 0,
            marginBottom: spacing,
        }),
        osIdRow: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: `${spacing}px ${spacing * 2}px`,
        }),
        osIdLabel: Object.freeze({
            ...typography.formLabelTight,
            fontSize: '18px',
        }),
        osIdValue: Object.freeze({
            ...typography.inlineHighlight,
            fontSize: '18px',
            fontWeight: 500,
        }),
        osIdActions: Object.freeze({
            display: 'inline-flex',
            flexWrap: 'wrap',
            gap: spacing,
            marginLeft: spacing * 0.5,
        }),
        copyButton: Object.freeze({
            textTransform: 'none',
            minWidth: 'auto',
        }),
        buttonText: Object.freeze({
            marginLeft: spacing * 0.5,
            fontSize: '14px',
        }),
    });
};
