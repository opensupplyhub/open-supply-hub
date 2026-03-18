import { getTypographyStyles } from '../../../../util/typographyStyles';
import COLOURS from '../../../../util/COLOURS';
import commonStyles from '../../commonStyles';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            ...commonStyles(theme).container,
            padding: '10px 20px 20px 20px',
        }),
        titleRow: Object.freeze({
            display: 'flex',
            flexWrap: 'nowrap',
            alignItems: 'center',
            marginBottom: spacing * 2,
            cursor: 'pointer',
        }),
        sectionTitle: Object.freeze({
            ...typography.sectionTitle,
            marginTop: 0,
            marginBottom: 0,
            marginRight: 0,
        }),
        infoButton: Object.freeze({
            marginLeft: spacing * 0.5,
            padding: spacing * 0.5,
            color: theme.palette.text.secondary,
            '&:hover': {
                color: theme.palette.text.primary,
                backgroundColor: theme.palette.action.hover,
            },
        }),
        switchWrap: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            marginLeft: 'auto',
        }),
        switchLabel: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.875rem',
        }),
        switch: Object.freeze({}),
        descriptionList: Object.freeze({
            marginTop: 0,
            '& > *:nth-child(2)': {
                [theme.breakpoints.up('md')]: {
                    paddingLeft: spacing * 2,
                    paddingRight: spacing * 2,
                },
            },
        }),
        descriptionItem: Object.freeze({
            display: 'block',
        }),
        itemRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
        }),
        itemHiddenTextWrap: Object.freeze({
            marginTop: spacing * 0.5,
            marginLeft: 20 + spacing,
        }),
        iconCrowdsourced: Object.freeze({
            flexShrink: 0,
            width: 20,
            height: 20,
            fontSize: 20,
            color: COLOURS.ORANGE,
        }),
        iconClaimed: Object.freeze({
            flexShrink: 0,
            width: 20,
            height: 20,
            fontSize: 20,
            color: COLOURS.DARK_GREEN,
        }),
        iconPartner: Object.freeze({
            flexShrink: 0,
            width: 20,
            height: 20,
            fontSize: 20,
            color: COLOURS.TEAL_GREEN,
        }),
        label: Object.freeze({
            ...typography.formLabelTight,
            fontSize: '1.125rem',
        }),
        labelClaimed: Object.freeze({
            ...typography.formLabelTight,
            fontSize: '1.125rem',
            color: COLOURS.DARK_GREEN,
        }),
        labelCrowdsourced: Object.freeze({
            ...typography.formLabelTight,
            fontSize: '1.125rem',
            color: COLOURS.ORANGE,
        }),
        labelPartner: Object.freeze({
            ...typography.formLabelTight,
            fontSize: '1.125rem',
            color: COLOURS.TEAL_GREEN,
        }),
        subsectionText: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.875rem',
            marginTop: 0,
            marginBottom: 0,
        }),
        learnMoreLink: Object.freeze({
            color: theme.palette.primary.main,
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            },
        }),
    });
};
