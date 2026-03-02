import { getTypographyStyles } from '../../../../util/typographyStyles';
import commonStyles from '../../commonStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            ...commonStyles(theme).container,
            marginBottom: spacing * 3,
            padding: '20px 20px 20px 36px',
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
        osIdValueWithTooltip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: spacing * 0.5,
        }),
        osIdValue: Object.freeze({
            ...typography.inlineHighlight,
            fontSize: '18px',
        }),
        osIdInfoButton: Object.freeze({
            padding: spacing * 0.5,
            color: theme.palette.text.secondary,
            '&:hover': {
                color: theme.palette.text.primary,
                backgroundColor: theme.palette.action.hover,
            },
        }),
        osIdActions: Object.freeze({
            display: 'inline-flex',
            flexWrap: 'wrap',
            marginLeft: 'auto',
        }),
        copyButtonWrap: Object.freeze({
            display: 'inline-flex',
            marginLeft: spacing * 2,
        }),
        copyButtonWrapFirst: Object.freeze({
            marginLeft: 0,
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
