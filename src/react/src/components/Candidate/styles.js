import COLOURS from '../../util/COLOURS';
import { getTypographyStyles } from '../../util/typographyStyles';
import {
    CANDIDATE_BADGE_COLOURS,
    CANDIDATE_STATE_CHIP_COLOURS,
    CANDIDATE_STATES,
} from '../../util/candidateCopy';

// Interim visuals, flagged for Design review (OSDEV-3192).
const stateChip = state => ({
    backgroundColor: CANDIDATE_STATE_CHIP_COLOURS[state].background,
    color: CANDIDATE_STATE_CHIP_COLOURS[state].text,
});

export const candidateBadgeStyles = theme => {
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        badge: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: spacing * 0.5,
            padding: `${spacing * 0.25}px ${spacing}px`,
            borderRadius: 12,
            border: `1px solid ${CANDIDATE_BADGE_COLOURS.border}`,
            backgroundColor: CANDIDATE_BADGE_COLOURS.background,
            color: CANDIDATE_BADGE_COLOURS.text,
            fontSize: '0.875rem',
            fontWeight: 600,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            whiteSpace: 'nowrap',
        }),
        badgeIcon: Object.freeze({
            fontSize: 16,
        }),
        stateChip: Object.freeze({
            display: 'inline-block',
            padding: `${spacing * 0.25}px ${spacing}px`,
            borderRadius: 12,
            fontSize: '0.875rem',
            fontWeight: 600,
            whiteSpace: 'nowrap',
        }),
        stateUnverified: stateChip(CANDIDATE_STATES.UNVERIFIED),
        stateDisputed: stateChip(CANDIDATE_STATES.DISPUTED),
        stateConfirmed: stateChip(CANDIDATE_STATES.CONFIRMED),
        stateRetirementPending: stateChip(CANDIDATE_STATES.RETIREMENT_PENDING),
    });
};

export const candidateHeadingStyles = theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        container: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing,
            padding: `0 ${spacing * 2.5}px ${spacing * 2}px 0`,
        }),
        badgeRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: spacing,
        }),
        provenance: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.95rem',
        }),
        provenanceItem: Object.freeze({
            display: 'inline',
            '& + &::before': {
                content: '" · "',
            },
        }),
        provenanceLabel: Object.freeze({
            fontWeight: 600,
            color: theme.palette.text.primary,
        }),
        note: Object.freeze({
            ...typography.bodyText,
            fontSize: '0.9rem',
            fontStyle: 'italic',
        }),
    });
};

export const candidateValidationPanelStyles = theme => {
    const typography = getTypographyStyles(theme);
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        root: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: COLOURS.WHITE,
            overflow: 'hidden',
        }),
        overlay: Object.freeze({
            position: 'absolute',
            top: spacing,
            right: spacing,
            zIndex: 1000,
            width: 300,
            maxWidth: 'calc(100% - 16px)',
            maxHeight: 'calc(100% - 16px)',
            overflowY: 'auto',
            borderRadius: 6,
            boxShadow: '0 4px 16px rgba(0,0,0,0.18)',
        }),
        inline: Object.freeze({
            boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
            width: '100%',
        }),
        header: Object.freeze({
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            gap: spacing,
            padding: `${spacing * 1.5}px ${spacing * 2}px`,
            backgroundColor: COLOURS.AMBER_50,
            borderBottom: `1px solid ${COLOURS.AMBER_300}`,
        }),
        headerText: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 0.5,
            flex: 1,
            minWidth: 0,
        }),
        title: Object.freeze({
            margin: 0,
            fontSize: '1.25rem',
            fontWeight: 600,
            lineHeight: 1.3,
            color: theme.palette.text.primary,
            fontFamily: theme.typography.fontFamily,
            '&:focus': {
                outline: 'none',
            },
            '&:focus-visible': {
                outline: `2px solid ${COLOURS.NAVY_BLUE}`,
                outlineOffset: 2,
            },
        }),
        intro: Object.freeze({
            ...typography.bodyText,
            fontSize: '1rem',
            lineHeight: 1.4,
        }),
        closeButton: Object.freeze({
            marginTop: -spacing * 0.5,
            marginRight: -spacing,
        }),
        section: Object.freeze({
            padding: `${spacing * 1.5}px ${spacing * 2}px`,
            borderBottom: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 0.75,
        }),
        sectionLast: Object.freeze({
            borderBottom: 'none',
        }),
        metaRow: Object.freeze({
            fontSize: '1rem',
            color: theme.palette.text.secondary,
        }),
        metaLabel: Object.freeze({
            fontWeight: 600,
            color: theme.palette.text.primary,
        }),
        stateRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: spacing,
        }),
        tally: Object.freeze({
            fontSize: '1rem',
            fontWeight: 500,
            color: theme.palette.text.primary,
        }),
        tallyDisputed: Object.freeze({
            color: COLOURS.PURPLE_TEXT,
            fontWeight: 600,
        }),
        stateDescription: Object.freeze({
            fontSize: '1rem',
            color: theme.palette.text.secondary,
        }),
        voteButtons: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 0.75,
        }),
        voteButton: Object.freeze({
            justifyContent: 'flex-start',
            textAlign: 'left',
            textTransform: 'none',
            fontSize: '1rem',
            fontWeight: 500,
            padding: `${spacing}px ${spacing * 1.5}px`,
            borderRadius: 4,
            border: `1px solid ${COLOURS.LIGHT_BORDER_GREY}`,
            backgroundColor: COLOURS.WHITE,
            color: theme.palette.text.primary,
            '&:hover': {
                backgroundColor: COLOURS.HOVER_GREY,
            },
        }),
        voteButtonSelected: Object.freeze({
            borderColor: COLOURS.NEAR_BLACK,
            backgroundColor: COLOURS.NEAR_BLACK,
            color: COLOURS.WHITE,
            '&:hover': {
                backgroundColor: COLOURS.DARK_SLATE_GREY,
            },
            '&$voteButtonDisabled': {
                backgroundColor: COLOURS.DARK_GREY,
                color: COLOURS.WHITE,
            },
        }),
        voteButtonDisabled: Object.freeze({}),
        voteButtonIcon: Object.freeze({
            fontSize: 20,
            marginRight: spacing,
        }),
        yourVoteTag: Object.freeze({
            marginLeft: 'auto',
            fontSize: '0.8rem',
            fontWeight: 600,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            opacity: 0.85,
        }),
        statusText: Object.freeze({
            fontSize: '1rem',
            color: theme.palette.text.secondary,
        }),
        statusClosed: Object.freeze({
            color: COLOURS.GREEN_TEXT,
            fontWeight: 600,
        }),
        statusRetired: Object.freeze({
            color: COLOURS.MATERIAL_RED,
            fontWeight: 600,
        }),
        statusError: Object.freeze({
            color: COLOURS.MATERIAL_RED,
        }),
        matchesTitle: Object.freeze({
            fontSize: '0.875rem',
            fontWeight: 600,
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            color: theme.palette.text.secondary,
        }),
        matchesList: Object.freeze({
            listStyle: 'none',
            margin: 0,
            padding: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing,
        }),
        matchItem: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
        }),
        matchName: Object.freeze({
            fontSize: '1rem',
            fontWeight: 500,
            color: COLOURS.NAVY_BLUE,
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            },
        }),
        matchMeta: Object.freeze({
            fontSize: '0.875rem',
            color: theme.palette.text.secondary,
        }),
        matchActions: Object.freeze({
            display: 'flex',
            flexWrap: 'wrap',
            gap: spacing * 0.5,
            marginTop: spacing * 0.5,
        }),
        matchButton: Object.freeze({
            textTransform: 'none',
            fontSize: '0.875rem',
            padding: `${spacing * 0.25}px ${spacing}px`,
            '&[aria-pressed="true"]': {
                backgroundColor: COLOURS.NAVY_BLUE,
                color: COLOURS.WHITE,
            },
        }),
        knowLink: Object.freeze({
            display: 'inline-flex',
            alignItems: 'center',
            gap: spacing * 0.5,
            fontSize: '1rem',
            fontWeight: 600,
            color: COLOURS.NAVY_BLUE,
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            },
        }),
        knowHint: Object.freeze({
            fontSize: '0.875rem',
            color: theme.palette.text.secondary,
        }),
        loading: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            padding: spacing,
        }),
    });
};

// --- Candidate review page (/candidates, OSDEV-3755) -----------------

export const candidateReviewPageStyles = theme => {
    const spacing = theme.spacing.unit ?? 8;
    const typography = getTypographyStyles(theme);
    return Object.freeze({
        root: Object.freeze({
            maxWidth: 1400,
            margin: '0 auto',
            padding: `${spacing * 3}px ${spacing * 2}px ${spacing * 6}px`,
        }),
        header: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing,
            marginBottom: spacing * 3,
        }),
        title: Object.freeze({
            fontSize: '32px',
            fontWeight: theme.typography.fontWeightSemiBold,
            margin: 0,
        }),
        intro: Object.freeze({
            ...typography.bodyText,
            fontSize: '1.125rem',
            maxWidth: 760,
        }),
        layout: Object.freeze({
            display: 'flex',
            gap: spacing * 3,
            alignItems: 'flex-start',
            [theme.breakpoints.down('sm')]: {
                flexDirection: 'column',
            },
        }),
        rail: Object.freeze({
            flex: '0 0 240px',
            [theme.breakpoints.down('sm')]: {
                flex: '1 1 auto',
                width: '100%',
            },
        }),
        main: Object.freeze({
            flex: '1 1 auto',
            minWidth: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 2,
        }),
        topRow: Object.freeze({
            display: 'flex',
            gap: spacing * 2,
            alignItems: 'stretch',
            [theme.breakpoints.down('md')]: {
                flexDirection: 'column',
            },
        }),
        mapColumn: Object.freeze({
            flex: '1 1 55%',
            minWidth: 0,
        }),
        panelColumn: Object.freeze({
            flex: '1 1 45%',
            minWidth: 0,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing,
        }),
        panelNav: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: spacing,
            flexWrap: 'wrap',
        }),
        panelPosition: Object.freeze({
            ...typography.bodyText,
            fontSize: '1rem',
            marginLeft: 'auto',
        }),
        panelPaper: Object.freeze({
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 8,
        }),
        summaryRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: spacing * 2,
            flexWrap: 'wrap',
        }),
        summary: Object.freeze({
            ...typography.bodyText,
            fontSize: '1.125rem',
        }),
        status: Object.freeze({
            padding: spacing * 3,
            textAlign: 'center',
        }),
        statusText: Object.freeze({
            ...typography.bodyText,
            fontSize: '1.125rem',
            marginBottom: spacing,
        }),
        loginNote: Object.freeze({
            padding: spacing * 3,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 2,
            alignItems: 'flex-start',
        }),
        loginNoteText: Object.freeze({
            ...typography.bodyText,
            fontSize: '1.125rem',
        }),
        button: Object.freeze({
            fontSize: '1rem',
        }),
    });
};

export const candidateListFiltersStyles = theme => {
    const spacing = theme.spacing.unit ?? 8;
    const typography = getTypographyStyles(theme);
    return Object.freeze({
        root: Object.freeze({
            padding: spacing * 2,
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 8,
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 2,
        }),
        title: Object.freeze({
            ...typography.formLabelTight,
            margin: 0,
        }),
        group: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 0.5,
        }),
        groupLabel: Object.freeze({
            fontSize: '0.875rem',
            fontWeight: 600,
            letterSpacing: '0.04em',
            textTransform: 'uppercase',
            color: theme.palette.text.secondary,
        }),
        checkbox: Object.freeze({
            padding: `${spacing * 0.25}px ${spacing}px`,
        }),
        checkboxLabel: Object.freeze({
            marginLeft: -spacing,
            marginRight: 0,
        }),
        checkboxLabelText: Object.freeze({
            fontSize: '1rem',
        }),
        helperText: Object.freeze({
            fontSize: '0.875rem',
        }),
        chip: Object.freeze({
            fontSize: '1rem',
        }),
        range: Object.freeze({
            display: 'flex',
            gap: spacing,
        }),
        rangeField: Object.freeze({
            flex: 1,
        }),
        hint: Object.freeze({
            ...typography.bodyText,
            fontSize: '1rem',
        }),
        areaRow: Object.freeze({
            display: 'flex',
            alignItems: 'center',
            gap: spacing,
            flexWrap: 'wrap',
        }),
        resetButton: Object.freeze({
            alignSelf: 'flex-start',
            textTransform: 'none',
            fontSize: '1rem',
        }),
    });
};

export const candidateListTableStyles = theme => {
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        root: Object.freeze({
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 8,
            overflow: 'hidden',
        }),
        scroll: Object.freeze({
            overflowX: 'auto',
        }),
        // MUI's dense cell padding (56px on the right) no longer fits
        // eight columns at body size; tighten it.
        headCell: Object.freeze({
            whiteSpace: 'nowrap',
            fontSize: '1rem',
            fontWeight: 600,
            padding: `${spacing}px ${spacing * 1.5}px`,
        }),
        row: Object.freeze({
            cursor: 'pointer',
            '&:hover': {
                backgroundColor: theme.palette.action.hover,
            },
        }),
        rowSelected: Object.freeze({
            backgroundColor: `${COLOURS.LIGHT_PURPLE} !important`,
        }),
        cell: Object.freeze({
            whiteSpace: 'nowrap',
            fontSize: '1rem',
            padding: `${spacing}px ${spacing * 1.5}px`,
        }),
        osIdLink: Object.freeze({
            color: COLOURS.PURPLE,
            fontWeight: 600,
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            },
        }),
        nearestName: Object.freeze({
            display: 'block',
            fontSize: '0.9375rem',
            color: theme.palette.text.secondary,
            maxWidth: 220,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
        }),
        muted: Object.freeze({
            color: theme.palette.text.secondary,
        }),
        loading: Object.freeze({
            display: 'flex',
            justifyContent: 'center',
            padding: spacing * 3,
        }),
        paginationCaption: Object.freeze({
            fontSize: '1rem',
        }),
    });
};

export const candidateListMapStyles = theme => {
    const spacing = theme.spacing.unit ?? 8;
    return Object.freeze({
        root: Object.freeze({
            position: 'relative',
            height: 360,
            border: `1px solid ${theme.palette.divider}`,
            borderRadius: 8,
            overflow: 'hidden',
            '& .leaflet-container': {
                height: '100%',
                width: '100%',
            },
        }),
        drawing: Object.freeze({
            userSelect: 'none',
            '& .leaflet-container': {
                cursor: 'crosshair',
            },
        }),
        controls: Object.freeze({
            display: 'flex',
            flexDirection: 'column',
            gap: spacing * 0.5,
        }),
        controlButton: Object.freeze({
            backgroundColor: theme.palette.common.white,
            textTransform: 'none',
            fontSize: '1rem',
            '&:hover': {
                backgroundColor: theme.palette.grey[100],
            },
        }),
        hint: Object.freeze({
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
            padding: `${spacing * 0.5}px ${spacing}px`,
            borderRadius: 4,
            fontSize: '1rem',
        }),
    });
};
