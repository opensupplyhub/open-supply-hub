import React, { useState, useEffect, useCallback } from 'react';
import { toast } from 'react-toastify';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Switch from '@material-ui/core/Switch';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';

import AppGrid from './AppGrid';
import apiRequest from '../util/apiRequest';
import {
    makeSpotlightFieldsURL,
    makeSpotlightVisibilityURL,
} from '../util/util';
import {
    SPOTLIGHT_NAME_RULES,
    SPOTLIGHT_DISPLAY_NAME_RULES,
    validateSpotlightInternalName,
    validateSpotlightDisplayName,
    getSpotlightFieldStatus,
} from '../util/spotlightFields';

const sectionStyle = { marginBottom: 32 };

// Pulls the first readable message out of an API error response.
const getErrorMessages = error => {
    const data = error && error.response && error.response.data;
    if (!data) return { general: 'Something went wrong. Please try again.' };
    if (Array.isArray(data)) return { general: data.join(' ') };
    if (data.detail) return { general: data.detail };
    return Object.keys(data).reduce(
        (messages, key) => ({
            ...messages,
            [key]: Array.isArray(data[key]) ? data[key].join(' ') : data[key],
        }),
        {},
    );
};

/**
 * The Spotlight tab in Settings. Spotlight partners create the fields that
 * describe their data, rename how a field is displayed, and switch fields on
 * or off once an admin has approved them. Fields can never be deleted.
 */
function SpotlightFieldsSettings() {
    const [loading, setLoading] = useState(true);
    const [summary, setSummary] = useState(null);
    const [name, setName] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [formErrors, setFormErrors] = useState({});
    const [notice, setNotice] = useState(null);
    const [edits, setEdits] = useState({});

    const handleError = error => {
        const messages = getErrorMessages(error);
        if (messages.general) {
            toast.error(messages.general, { position: 'bottom-left' });
        }
        return messages;
    };

    const load = useCallback(() => {
        setLoading(true);
        apiRequest
            .get(makeSpotlightFieldsURL())
            .then(({ data }) => setSummary(data))
            .catch(handleError)
            .finally(() => setLoading(false));
    }, []);

    useEffect(() => load(), [load]);

    const submitNewField = e => {
        e.preventDefault();
        const errors = {};
        const nameError = validateSpotlightInternalName(name);
        const displayError = validateSpotlightDisplayName(displayName);
        if (nameError) errors.name = nameError;
        if (displayError) errors.display_name = displayError;
        setFormErrors(errors);
        if (Object.keys(errors).length > 0) return;

        setLoading(true);
        apiRequest
            .post(makeSpotlightFieldsURL(), {
                name,
                display_name: displayName.trim(),
            })
            .then(({ data }) => {
                setSummary(data);
                setNotice(data.message);
                setName('');
                setDisplayName('');
            })
            .catch(error => setFormErrors(handleError(error)))
            .finally(() => setLoading(false));
    };

    const updateField = (fieldName, changes) => {
        setLoading(true);
        apiRequest
            .patch(makeSpotlightFieldsURL(fieldName), changes)
            .then(({ data }) => {
                setSummary(data);
                setEdits(previous => {
                    const { [fieldName]: removed, ...rest } = previous;
                    return rest;
                });
            })
            .catch(handleError)
            .finally(() => setLoading(false));
    };

    const updateVisibility = changes => {
        setLoading(true);
        apiRequest
            .patch(makeSpotlightVisibilityURL(), changes)
            .then(({ data }) => setSummary(data))
            .catch(handleError)
            .finally(() => setLoading(false));
    };

    if (!summary) {
        return (
            <AppGrid title="Spotlight">
                {loading ? (
                    <CircularProgress />
                ) : (
                    <Typography>
                        We could not load your Spotlight fields.
                    </Typography>
                )}
            </AppGrid>
        );
    }

    return (
        <AppGrid title="Spotlight">
            <div style={sectionStyle}>
                <Typography paragraph>
                    Create the fields that describe your data on OS Hub. New
                    fields stay inactive until the OS Hub team approves them.
                    Once approved, you can switch them on yourself
                    {summary.go_live_date
                        ? ', or they go live automatically on the date we set.'
                        : '.'}
                </Typography>
                {summary.go_live_date && (
                    <Typography paragraph>
                        <strong>Go-live date: {summary.go_live_date}.</strong>{' '}
                        {summary.go_live_pending
                            ? 'Until then you cannot switch fields on yourself; ' +
                              'they will all go live on this date.'
                            : 'This date has passed.'}
                    </Typography>
                )}
                {notice && (
                    <Typography
                        paragraph
                        role="status"
                        style={{ fontWeight: 600 }}
                    >
                        {notice}
                    </Typography>
                )}
            </div>

            <form
                onSubmit={submitNewField}
                style={sectionStyle}
                noValidate
                aria-label="Add a Spotlight field"
            >
                <Typography variant="title" gutterBottom>
                    Add a field
                </Typography>
                <TextField
                    id="spotlight-internal-name"
                    label="Internal name"
                    value={name}
                    onChange={e => setName(e.target.value)}
                    error={Boolean(formErrors.name)}
                    helperText={formErrors.name || SPOTLIGHT_NAME_RULES}
                    fullWidth
                    margin="normal"
                    inputProps={{ maxLength: 50 }}
                />
                <TextField
                    id="spotlight-display-name"
                    label="Display name"
                    value={displayName}
                    onChange={e => setDisplayName(e.target.value)}
                    error={Boolean(formErrors.display_name)}
                    helperText={
                        formErrors.display_name || SPOTLIGHT_DISPLAY_NAME_RULES
                    }
                    fullWidth
                    margin="normal"
                    inputProps={{ maxLength: 50 }}
                />
                <Button
                    type="submit"
                    variant="contained"
                    color="primary"
                    disabled={loading}
                >
                    Submit field
                </Button>
            </form>

            <div style={sectionStyle}>
                <Typography variant="title" gutterBottom>
                    Your fields
                </Typography>
                {summary.fields.length === 0 ? (
                    <Typography>You have not added any fields yet.</Typography>
                ) : (
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Display name</TableCell>
                                <TableCell>Internal name</TableCell>
                                <TableCell>Status</TableCell>
                                <TableCell>Active</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {summary.fields.map(field => {
                                const edited = edits[field.name];
                                const current =
                                    edited === undefined
                                        ? field.display_name
                                        : edited;
                                const blockedByDate =
                                    !field.active && summary.go_live_pending;
                                return (
                                    <TableRow key={field.name}>
                                        <TableCell>
                                            <TextField
                                                value={current}
                                                onChange={e =>
                                                    setEdits(previous => ({
                                                        ...previous,
                                                        [field.name]:
                                                            e.target.value,
                                                    }))
                                                }
                                                error={Boolean(
                                                    edited !== undefined &&
                                                        validateSpotlightDisplayName(
                                                            edited,
                                                        ),
                                                )}
                                                helperText={
                                                    edited !== undefined
                                                        ? validateSpotlightDisplayName(
                                                              edited,
                                                          )
                                                        : null
                                                }
                                                inputProps={{
                                                    maxLength: 50,
                                                    'aria-label': `Display name for ${field.name}`,
                                                }}
                                            />
                                            {edited !== undefined &&
                                                edited !==
                                                    field.display_name && (
                                                    <Button
                                                        size="small"
                                                        disabled={
                                                            loading ||
                                                            Boolean(
                                                                validateSpotlightDisplayName(
                                                                    edited,
                                                                ),
                                                            )
                                                        }
                                                        onClick={() =>
                                                            updateField(
                                                                field.name,
                                                                {
                                                                    display_name: edited.trim(),
                                                                },
                                                            )
                                                        }
                                                    >
                                                        Save
                                                    </Button>
                                                )}
                                        </TableCell>
                                        <TableCell>
                                            <code>{field.name}</code>
                                        </TableCell>
                                        <TableCell>
                                            {getSpotlightFieldStatus(field)}
                                        </TableCell>
                                        <TableCell>
                                            <Switch
                                                checked={field.active}
                                                disabled={
                                                    loading ||
                                                    !field.approved ||
                                                    blockedByDate
                                                }
                                                onChange={e =>
                                                    updateField(field.name, {
                                                        active:
                                                            e.target.checked,
                                                    })
                                                }
                                                inputProps={{
                                                    'aria-label': `Active: ${field.name}`,
                                                }}
                                            />
                                        </TableCell>
                                    </TableRow>
                                );
                            })}
                        </TableBody>
                    </Table>
                )}
                <Typography variant="caption" style={{ marginTop: 8 }}>
                    Fields cannot be deleted. Switch a field off to hide it
                    everywhere on OS Hub.
                </Typography>
            </div>

            {summary.can_control_visibility && (
                <div style={sectionStyle}>
                    <Typography variant="title" gutterBottom>
                        Where your fields appear
                    </Typography>
                    <FormControlLabel
                        control={
                            <Switch
                                checked={summary.available_in_api}
                                disabled={loading}
                                onChange={e =>
                                    updateVisibility({
                                        available_in_api: e.target.checked,
                                    })
                                }
                            />
                        }
                        label="Show in the API"
                    />
                    <FormControlLabel
                        control={
                            <Switch
                                checked={summary.available_in_data_downloads}
                                disabled={loading}
                                onChange={e =>
                                    updateVisibility({
                                        available_in_data_downloads:
                                            e.target.checked,
                                    })
                                }
                            />
                        }
                        label="Show in data downloads"
                    />
                </div>
            )}
        </AppGrid>
    );
}

export default SpotlightFieldsSettings;
