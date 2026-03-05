import COLOURS from '../../../../util/COLOURS';
import { getTypographyStyles } from '../../../../util/typographyStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        osIdRow: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            alignItems: 'center',
            gap: `${spacing}px ${spacing * 2}px`,
            padding: '12px',
            border: `1px solid ${COLOURS.LIGHT_PURPLE_BORDER}`,
            backgroundColor: 'rgba(128, 64, 191, 0.05)',
            marginBottom: theme.spacing.unit * 2,
        }),
        osIdValueWithTooltip: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: spacing * 0.5,
        }),
        osIdLabel: Object.freeze({
            fontWeight: 'bold',
            ...typography.formLabelTight,
        }),
        osIdValue: Object.freeze({
            fontWeight: 'bold',
            fontSize: '1.75rem',
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
            backgroundColor: COLOURS.WHITE,
            display: 'inline-flex',
            marginLeft: spacing * 2,
        }),
        copyButtonWrapFirst: Object.freeze({
            backgroundColor: COLOURS.WHITE,
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
