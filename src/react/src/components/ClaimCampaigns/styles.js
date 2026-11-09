import COLOURS from '../../util/COLOURS';
import { OARFont } from '../../util/constants';

export const claimCampaignsStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            maxWidth: '1072px',
            margin: '0 auto',
            padding: '24px 16px 64px',
        }),
        title: Object.freeze({
            fontWeight: theme.typography.fontWeightBold,
            marginBottom: '4px',
        }),
        subtitle: Object.freeze({
            color: COLOURS.DARK_GREY,
            marginBottom: '24px',
        }),
        pageHeader: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px',
        }),
        createdBanner: Object.freeze({
            padding: '12px 16px',
            marginBottom: '16px',
            borderLeft: `4px solid ${COLOURS.MATERIAL_GREEN}`,
        }),
        campaignCard: Object.freeze({
            padding: '20px 24px',
            marginBottom: '16px',
        }),
        campaignHeader: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
        }),
        campaignName: Object.freeze({
            fontWeight: theme.typography.fontWeightBold,
            fontSize: '24px',
            display: 'block',
        }),
        campaignMeta: Object.freeze({
            color: COLOURS.DARK_GREY,
        }),
        codeBox: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 8px 4px 12px',
            border: `1px dashed ${COLOURS.PURPLE}`,
            borderRadius: '6px',
            backgroundColor: COLOURS.PURPLE_TINT,
        }),
        codeLabel: Object.freeze({
            color: COLOURS.DARK_GREY,
        }),
        code: Object.freeze({
            fontFamily: 'monospace',
            fontWeight: 600,
            color: COLOURS.PURPLE_TEXT,
        }),
        kpiRow: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            gap: '12px',
            margin: '20px 0 12px',
        }),
        kpiTile: Object.freeze({
            flex: '1 1 140px',
            border: `1px solid ${COLOURS.GREY}`,
            borderRadius: '8px',
            padding: '14px 16px',
        }),
        kpiValue: Object.freeze({
            display: 'block',
            fontSize: '28px',
            fontWeight: theme.typography.fontWeightBold,
            lineHeight: 1.2,
        }),
        kpiLabel: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            color: COLOURS.DARK_GREY,
        }),
        statusSquare: Object.freeze({
            display: 'inline-block',
            width: '10px',
            height: '10px',
            borderRadius: '2px',
            flexShrink: 0,
        }),
        progressPanel: Object.freeze({
            border: `1px solid ${COLOURS.GREY}`,
            borderRadius: '8px',
            padding: '14px 16px',
            marginBottom: '8px',
        }),
        progressHeader: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '10px',
        }),
        progressTitle: Object.freeze({
            fontWeight: theme.typography.fontWeightBold,
        }),
        segmentBar: Object.freeze({
            display: 'flex',
            height: '22px',
            borderRadius: '4px',
            overflow: 'hidden',
            gap: '2px',
        }),
        segment: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: COLOURS.WHITE,
            fontSize: '12px',
            fontWeight: 600,
            minWidth: '18px',
        }),
        legend: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            gap: '16px',
            marginTop: '10px',
            color: COLOURS.DARK_GREY,
        }),
        legendItem: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
        }),
        chipContent: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
        }),
        statusDot: Object.freeze({
            display: 'inline-block',
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            flexShrink: 0,
        }),
        tableTools: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            margin: '16px 0 8px',
        }),
        // Matches the page titles rendered by AppGrid (e.g. My Lists).
        sectionTitle: Object.freeze({
            fontFamily: OARFont,
            fontWeight: 'normal',
            fontSize: '32px',
            margin: 0,
        }),
        tableToolsActions: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '16px',
        }),
        modeToggle: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
        }),
        modeLabel: Object.freeze({
            color: COLOURS.DARK_GREY,
            marginRight: '4px',
        }),
        modeButton: Object.freeze({
            minWidth: '0',
            boxShadow: 'none',
        }),
        tableWrap: Object.freeze({
            overflowX: 'auto',
        }),
        // Fixed layout so long facility names wrap instead of pushing the
        // other columns right; the contact column gets the spare width.
        supplierTable: Object.freeze({
            tableLayout: 'fixed',
            minWidth: '760px',
        }),
        colFacility: Object.freeze({ width: '28%', padding: '8px 12px' }),
        colOsId: Object.freeze({ width: '17%', padding: '8px 12px' }),
        colCountry: Object.freeze({ width: '9%', padding: '8px 12px' }),
        colStatus: Object.freeze({ width: '16%', padding: '8px 12px' }),
        colContact: Object.freeze({ width: '30%', padding: '8px 12px' }),
        cell: Object.freeze({
            padding: '8px 12px',
            overflowWrap: 'anywhere',
        }),
        headerWithHelp: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: '4px',
        }),
        helpIcon: Object.freeze({
            fontSize: '18px',
            color: COLOURS.DARK_GREY,
            cursor: 'help',
        }),
        emailInvite: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: '2px',
        }),
        emailInviteRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
        }),
        emailField: Object.freeze({
            flexGrow: 1,
            minWidth: '0',
        }),
        invitedNote: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontSize: '13px',
        }),
        inviteError: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            fontSize: '13px',
        }),
        statusClaimed: Object.freeze({
            backgroundColor: COLOURS.LIGHT_GREEN,
            color: COLOURS.GREEN_TEXT,
        }),
        statusPending: Object.freeze({
            backgroundColor: COLOURS.LIGHT_AMBER,
            color: COLOURS.ORANGE,
        }),
        statusUnclaimed: Object.freeze({
            backgroundColor: COLOURS.LIGHTEST_GREY,
            color: COLOURS.DARK_GREY,
        }),
        emptyMessage: Object.freeze({
            padding: '48px 16px',
            textAlign: 'center',
            color: COLOURS.DARK_GREY,
        }),
    });

export const newClaimCampaignStyles = theme =>
    Object.freeze({
        container: Object.freeze({
            maxWidth: '1072px',
            margin: '0 auto',
            padding: '24px 16px 64px',
        }),
        title: Object.freeze({
            fontWeight: theme.typography.fontWeightBold,
            marginBottom: '4px',
        }),
        subtitle: Object.freeze({
            color: COLOURS.DARK_GREY,
            marginBottom: '24px',
        }),
        message: Object.freeze({
            padding: '48px 16px',
            textAlign: 'center',
        }),
        stepHeading: Object.freeze({
            fontWeight: theme.typography.fontWeightBold,
            fontSize: '18px',
            margin: '24px 0 8px',
        }),
        panel: Object.freeze({
            padding: '16px 24px',
        }),
        sourceOptions: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
        }),
        sourceHint: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontSize: '14px',
            margin: '-8px 0 8px 32px',
        }),
        pickedHeading: Object.freeze({
            fontWeight: theme.typography.fontWeightMedium,
            margin: '24px 0 8px',
        }),
        listOption: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
        }),
        listName: Object.freeze({
            fontWeight: theme.typography.fontWeightMedium,
        }),
        publicChip: Object.freeze({
            height: '24px',
        }),
        privateChip: Object.freeze({
            height: '24px',
            backgroundColor: COLOURS.PURPLE_TINT,
            color: COLOURS.MATERIAL_PURPLE,
        }),
        toolbar: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '8px',
            marginBottom: '8px',
        }),
        grow: Object.freeze({
            flexGrow: 1,
        }),
        tableWrap: Object.freeze({
            overflowX: 'auto',
            maxHeight: '480px',
            overflowY: 'auto',
        }),
        country: Object.freeze({
            color: COLOURS.DARK_GREY,
            marginLeft: '8px',
        }),
        fine: Object.freeze({
            color: COLOURS.DARK_GREY,
            fontSize: '14px',
            marginTop: '8px',
        }),
        createRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '16px',
        }),
        nameField: Object.freeze({
            minWidth: '320px',
            flexGrow: 1,
        }),
        error: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            marginTop: '8px',
        }),
    });

export const campaignSupplierSearchStyles = theme =>
    Object.freeze({
        ...newClaimCampaignStyles(theme),
        // The public search filters, laid out in two columns.
        filters: Object.freeze({
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            columnGap: '24px',
        }),
        searchRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '16px',
            margin: '16px 0 8px',
        }),
    });

export default claimCampaignsStyles;
