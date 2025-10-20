import React from 'react';
import { func, object } from 'prop-types';
import { withStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import TextField from '@material-ui/core/TextField';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Business from '@material-ui/icons/Business';
import Award from '@material-ui/icons/Star';
import NaturePeople from '@material-ui/icons/NaturePeople';

import COLOURS from '../../../util/COLOURS';

const profileStepStyles = theme =>
    Object.freeze({
        card: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            boxShadow: 'none',
            border: `1px solid ${COLOURS.GREY}`,
        }),
        cardHeader: Object.freeze({
            backgroundColor: '#f9fafb',
            paddingTop: theme.spacing.unit * 2,
            paddingBottom: theme.spacing.unit * 2,
        }),
        headerIcon: Object.freeze({
            marginRight: theme.spacing.unit,
            verticalAlign: 'middle',
            fontSize: '1.25rem',
        }),
        content: Object.freeze({
            padding: theme.spacing.unit * 3,
        }),
        expansionPanel: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
            boxShadow: 'none',
            border: `1px solid ${COLOURS.GREY}`,
            '&:before': {
                display: 'none',
            },
        }),
        expansionPanelSummary: Object.freeze({
            backgroundColor: '#f9fafb',
            paddingTop: theme.spacing.unit * 1.5,
            paddingBottom: theme.spacing.unit * 1.5,
        }),
        sectionIcon: Object.freeze({
            marginRight: theme.spacing.unit,
            color: theme.palette.primary.main,
            fontSize: '1.25rem',
        }),
        sectionTitle: Object.freeze({
            fontWeight: 600,
            fontSize: '1rem',
        }),
        field: Object.freeze({
            marginBottom: theme.spacing.unit * 2,
        }),
    });

const ProfileStep = ({ classes, formData, handleChange }) => (
    <Grid container spacing={24}>
        <Grid item xs={12}>
            <Card className={classes.card}>
                <CardHeader
                    className={classes.cardHeader}
                    title={
                        <Typography variant="h6">
                            <Business className={classes.headerIcon} />
                            Open Supply Hub Profile
                        </Typography>
                    }
                    subheader="All fields are optional. Provide as much detail as you can."
                />
                <CardContent className={classes.content}>
                    {/* Production Location Overview */}
                    <ExpansionPanel className={classes.expansionPanel}>
                        <ExpansionPanelSummary
                            expandIcon={<ExpandMoreIcon />}
                            className={classes.expansionPanelSummary}
                        >
                            <Business className={classes.sectionIcon} />
                            <Typography className={classes.sectionTitle}>
                                Production Location Overview
                            </Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            <Grid container spacing={16}>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Facility Name"
                                        value={formData.facilityName || ''}
                                        onChange={e =>
                                            handleChange(
                                                'facilityName',
                                                e.target.value,
                                            )
                                        }
                                        className={classes.field}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Facility Phone"
                                        value={formData.facilityPhone || ''}
                                        onChange={e =>
                                            handleChange(
                                                'facilityPhone',
                                                e.target.value,
                                            )
                                        }
                                        className={classes.field}
                                    />
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField
                                        fullWidth
                                        multiline
                                        rows={3}
                                        label="Description"
                                        value={formData.description || ''}
                                        onChange={e =>
                                            handleChange(
                                                'description',
                                                e.target.value,
                                            )
                                        }
                                        className={classes.field}
                                    />
                                </Grid>
                            </Grid>
                        </ExpansionPanelDetails>
                    </ExpansionPanel>

                    {/* Company Information */}
                    <ExpansionPanel className={classes.expansionPanel}>
                        <ExpansionPanelSummary
                            expandIcon={<ExpandMoreIcon />}
                            className={classes.expansionPanelSummary}
                        >
                            <Business className={classes.sectionIcon} />
                            <Typography className={classes.sectionTitle}>
                                Company Information
                            </Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            <Grid container spacing={16}>
                                <Grid item xs={12}>
                                    <TextField
                                        fullWidth
                                        label="Parent Company Name"
                                        value={formData.parentCompanyName || ''}
                                        onChange={e =>
                                            handleChange(
                                                'parentCompanyName',
                                                e.target.value,
                                            )
                                        }
                                        className={classes.field}
                                    />
                                </Grid>
                            </Grid>
                        </ExpansionPanelDetails>
                    </ExpansionPanel>

                    {/* Operations & Capabilities */}
                    <ExpansionPanel className={classes.expansionPanel}>
                        <ExpansionPanelSummary
                            expandIcon={<ExpandMoreIcon />}
                            className={classes.expansionPanelSummary}
                        >
                            <Business className={classes.sectionIcon} />
                            <Typography className={classes.sectionTitle}>
                                Operations & Capabilities
                            </Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            <Grid container spacing={16}>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="Number of Workers"
                                        value={formData.numberOfWorkers || ''}
                                        onChange={e =>
                                            handleChange(
                                                'numberOfWorkers',
                                                e.target.value,
                                            )
                                        }
                                        className={classes.field}
                                    />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField
                                        fullWidth
                                        label="% Female Workers"
                                        value={formData.femaleWorkers || ''}
                                        onChange={e =>
                                            handleChange(
                                                'femaleWorkers',
                                                e.target.value,
                                            )
                                        }
                                        className={classes.field}
                                    />
                                </Grid>
                            </Grid>
                        </ExpansionPanelDetails>
                    </ExpansionPanel>

                    {/* Compliance & Partnerships */}
                    <ExpansionPanel className={classes.expansionPanel}>
                        <ExpansionPanelSummary
                            expandIcon={<ExpandMoreIcon />}
                            className={classes.expansionPanelSummary}
                        >
                            <Award className={classes.sectionIcon} />
                            <Typography className={classes.sectionTitle}>
                                Compliance & Partnerships
                            </Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            <Typography variant="body2" color="textSecondary">
                                Affiliations and certifications will be
                                implemented in future tasks.
                            </Typography>
                        </ExpansionPanelDetails>
                    </ExpansionPanel>

                    {/* Environmental Data */}
                    <ExpansionPanel className={classes.expansionPanel}>
                        <ExpansionPanelSummary
                            expandIcon={<ExpandMoreIcon />}
                            className={classes.expansionPanelSummary}
                        >
                            <NaturePeople className={classes.sectionIcon} />
                            <Typography className={classes.sectionTitle}>
                                Environmental Data
                            </Typography>
                        </ExpansionPanelSummary>
                        <ExpansionPanelDetails>
                            <Typography variant="body2" color="textSecondary">
                                Environmental data fields will be implemented in
                                future tasks.
                            </Typography>
                        </ExpansionPanelDetails>
                    </ExpansionPanel>

                    <Typography variant="caption" color="textSecondary">
                        Note: This is placeholder content. Actual form fields
                        will be implemented in future tasks.
                    </Typography>
                </CardContent>
            </Card>
        </Grid>
    </Grid>
);

ProfileStep.propTypes = {
    classes: object.isRequired,
    formData: object.isRequired,
    handleChange: func.isRequired,
};

export default withStyles(profileStepStyles)(ProfileStep);
