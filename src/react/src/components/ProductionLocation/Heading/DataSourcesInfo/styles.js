import { getTypographyStyles } from '../../../../util/typographyStyles';
import COLOURS from '../../../../util/COLOURS';

export default theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            backgroundColor: theme.palette.background.paper,
            paddingTop: spacing,
            paddingBottom: spacing * 2,
        }),
        titleRow: Object.freeze({
            display: 'flex',
            flexWrap: 'nowrap',
            alignItems: 'center',
            marginBottom: spacing * 2,
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
        descriptionList: Object.freeze({
            marginTop: 0,
        }),
        descriptionItem: Object.freeze({
            display: 'block',
        }),
        itemContent: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            gap: spacing * 2,
        }),
        itemText: Object.freeze({
            flex: 1,
            minWidth: 0,
        }),
        iconCrowdsourced: Object.freeze({
            flexShrink: 0,
            marginTop: 2,
            fontSize: 20,
            color: COLOURS.DARK_GREY,
        }),
        iconClaimed: Object.freeze({
            flexShrink: 0,
            marginTop: 2,
            fontSize: 20,
            color: COLOURS.DARK_GREEN,
        }),
        iconPartner: Object.freeze({
            flexShrink: 0,
            marginTop: 2,
            fontSize: 20,
            color: COLOURS.MATERIAL_BLUE,
        }),
        label: Object.freeze({
            ...typography.formLabelTight,
            fontSize: '18px',
        }),
        description: Object.freeze({
            ...typography.sectionDescription,
            ...typography.bodyText,
            marginTop: spacing * 0.5,
            marginBottom: 0,
        }),
    });
};
